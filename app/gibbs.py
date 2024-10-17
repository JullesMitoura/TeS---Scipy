import pandas as pd
import numpy as np
from scipy.optimize import minimize
from app.EoS import fug

# Constantes globais
R = 8.314  # J/mol·K
T0 = 298.15  # Temperatura de referência em Kelvin
epsilon = 1e-05  # Pequeno valor para ajustar o limite superior

def GIBBS(data, Pmin, Pmax, Tmin, Tmax, eq, npressure, ntemp, inhibited_component=None):
    df = pd.read_csv(data, index_col=0).dropna()
    species = df.columns[df.columns.get_loc("C"):]
    dic = df.to_dict(orient='index')
    Components = df.index.tolist()

    def gibbs0(T, components):
        results = []
        log_T = np.log(T)  # Calcula log(T) uma única vez
        for component in components.values():
            delta_G_standard = component.get('∆Gf298', 0)
            delta_H_standard = component.get('∆Hf298', 0)
            a = component.get('a', 0)
            b = component.get('b', 0)
            c = component.get('c', 0)
            d = component.get('d', 0)

            aux = (1/T0 - 1/T) * delta_H_standard + R * (
                a * (log_T - np.log(T0) + T0 / T - 1) +
                (b / 2) * (-2 * T0 + (T0**2) / T + T) +
                (c / 3) * ((T**2 - T0**2) / 2 - (T0**3) * (-1/T + 1/T0)) +
                d * ((-T0 + T) / (T0 * T0 * T) + 1/(2*T*T) - 1/(2*T0*T0))
            )
            mu_i = T * (delta_G_standard / T0 - aux)
            results.append(mu_i)

        return np.array(results)

    def contar_elementos(lista1, lista2, bib):
        return np.array([[bib.get(mol, {}).get(elem, 0) for elem in lista1] for mol in lista2])

    A = contar_elementos(species.tolist(), Components, dic)

    def element_balance(n, n0, A):
        return np.dot(n, A) - np.dot(n0, A)

    n0 = df['initial'].values  # Converte diretamente para NumPy array
    cons = [{'type': 'eq', 'fun': element_balance, 'args': (n0, A)}]

    # Calcula 'max_species' diretamente
    max_species = np.dot(n0, df[species].values)

    # Criação das 'bounds' com vetorização
    bnds_aux = []
    for i, comp in enumerate(Components):
        if comp == inhibited_component:
            bnds_aux.append((1e-15, epsilon))
        else:
            a = np.multiply(1 / np.where(A[i] != 0, A[i], np.inf), max_species)
            upper_bound = np.min(a[a > 0]) if a[a > 0].size > 0 else epsilon
            bnds_aux.append((1e-15, max(upper_bound, epsilon)))

    bnds = tuple(bnds_aux)

    def gibbs(n, T, P):
        # Evita que os valores em 'n' sejam negativos
        n = np.clip(n, 1e-20, None)

        # Calcular Gibbs para sólidos
        solid_indices = [i for i, comp in enumerate(Components) if dic[comp]['Phase'] == 's']
        mi_solid = gibbs0(T, {comp: dic[comp] for comp in np.array(Components)[solid_indices]}) * n[solid_indices]

        # Calcular Gibbs para gases
        gas_indices = [i for i, comp in enumerate(Components) if dic[comp]['Phase'] == 'g']
        n_gases = n[gas_indices]
        dic_gases = {comp: dic[comp] for comp in np.array(Components)[gas_indices]}
        phii = fug(T, P, eq, n_gases, **dic_gases)
        mi_gas = gibbs0(T, dic_gases) + R * T * (np.log(phii) + np.log(n_gases / np.sum(n_gases)) + np.log(P))

        return np.sum(mi_solid) + np.sum(mi_gas * n_gases)

    # Define intervalos de P e T
    P = np.round(np.linspace(Pmin, Pmax, npressure), 2)
    T = np.round(np.linspace(Tmin, Tmax, ntemp), 2)

    init = [(low + high) * 0.6 / 2 for low, high in bnds]

    # Otimização
    results, pressure, temperature = [], [], []
    for p in P:
        for t in T:
            sol = minimize(gibbs, init, args=(t, p), bounds=bnds, method='trust-constr', constraints=cons, options={'disp': False, 'maxiter': 1000})
            results.append(sol.x)
            pressure.append(p)
            temperature.append(t)

    results_df = pd.DataFrame(results, columns=df.index)
    results_df['Temperature (K)'] = temperature
    results_df['Pressure (bar)'] = pressure

    return results_df