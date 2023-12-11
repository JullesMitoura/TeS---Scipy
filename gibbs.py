import pandas as pd
import numpy as np
from scipy.optimize import minimize
from EoS import fug

def GIBBS(data,Pmin,Pmax,Tmin,Tmax,eq,npressure,ntemp,inhibited_component=None):
    df = pd.read_csv(data, index_col = 0).dropna()
    species = df.columns[df.columns.get_loc("C"):]
    dic = df.to_dict(orient='index')
    Components = df.index.tolist()


    def gibbs0(T, **components):
        R = 8.314  # J/mol·K
        T0 = 298.15  # Temperatura de referência em Kelvin
        
        results = []

        for component in components.values():
            delta_G_standard = component.get('∆Gf298', 0)
            delta_H_standard = component.get('∆Hf298', 0)
            a = component.get('a', 0)
            b = component.get('b', 0)
            c = component.get('c', 0)
            d = component.get('d', 0)

        
            aux = (1/T0-1/T)*delta_H_standard+R*(a*(np.log(T)-np.log(T0)+T0/T-1)+(b/2)*(-2*T0+(T0**2)/T+T)+(c/3)*((T*T-T0*T0)/2-(T0**3)*(-1/T+1/T0))+d*((-T0+T)/(T0*T0*T)+1/(2*T*T)-1/(2*T0*T0)))

            # Calculating mu_i using the provided formula
            mu_i = T*(delta_G_standard/T0-aux)
            
            results.append(mu_i)

        return results

    def contar_elementos(lista1, lista2, bib):
        # Inicializando a matriz de resultados com zeros
        resultados = np.zeros((len(lista2), len(lista1)), dtype=int)
        
        # Preenchendo a matriz com a contagem de elementos
        for i, mol in enumerate(lista2):
            for j, elem in enumerate(lista1):
                resultados[i, j] = bib.get(mol, {}).get(elem, 0)

        return np.array(resultados)
    A = contar_elementos(species.tolist(), Components, dic)

    def element_balance(n, n0, A):
        
        res = np.matmul(n, A) - np.matmul(n0, A)
        return res

    n0 = df['initial'].tolist()
    cons = [{'type': 'eq', 'fun': element_balance, 'args': [n0,A]}]

    for i in species.tolist():
        locals()[i] = np.dot(n0,df[[i.replace('_max', '')]])


    max_species = []
    for i in species:
        max_species.append(np.dot(n0,df[i]))

    epsilon = 1e-05  # Valor muito pequeno para ajustar o limite superior se for zero

    bnds_aux = []
    for i, comp in enumerate(Components):
        if comp == inhibited_component:
            bnds_aux.append((1e-15, epsilon))
        else:
            # O código existente para calcular os limites
            a = np.multiply(([1/x if x != 0 else 0 for x in A[i]]), max_species)
            a_aux = [x for x in a if x > 0]
            
            if a_aux:
                upper_bound = min(a_aux)
                upper_bound = epsilon if upper_bound == 0 else upper_bound
                lower_bound = 1e-15
                bnds_aux.append((lower_bound, upper_bound))
            else:
                bnds_aux.append((1e-15, epsilon))  # Ajuste para garantir que o limite superior seja sempre maior que o limite inferior

    bnds = tuple(bnds_aux)


    def gibbs(n, T, P):
        R = 8.314  # J/mol·K
        P0 = 1  # standard pressure in bar

        for i in range(n.shape[0]):
            if n[i] <= 0:
                n[i] = 1e-20

        # Calculando Gibbs para sólidos
        solid_indices = [i for i, comp in enumerate(Components) if dic[comp]['Phase'] == 's']
        n_solids = n[solid_indices]
        dfg_solid = np.array(gibbs0(T, **{comp: dic[comp] for comp in np.array(Components)[solid_indices]}))
        mi_solid = dfg_solid * n_solids

        # Calculando Gibbs para gases
        gas_indices = [i for i, comp in enumerate(Components) if dic[comp]['Phase'] == 'g']
        n_gases = n[gas_indices]
        dic_gases = {comp: propriedades for comp, propriedades in dic.items() if propriedades['Phase'] == 'g'}
        phii = fug(T, P, eq, n_gases, **dic_gases)
        dfg_gas = np.array(gibbs0(T, **{comp: dic[comp] for comp in np.array(Components)[gas_indices]}))
        mi_gas = dfg_gas + R * T * (np.log(phii) + np.log(n_gases / np.sum(n_gases)) + np.log(P))

        # Calculando a energia de Gibbs total
        total_gibbs = np.sum(mi_solid) + np.sum(mi_gas * n_gases)

        return total_gibbs



    P = [round(P, 2) for P in np.linspace(Pmin, Pmax, npressure)]

    T = [round(T, 2) for T in np.linspace(Tmin, Tmax, ntemp)]

    result = []
    pressure = []
    temperature = []

    init = [(low + high)*0.3 / 2 for low, high in bnds]
    previous_solution = None

    def positive_constraint(n):
        return n - 1e-15
    
    cons.append({'type': 'ineq', 'fun': positive_constraint})


    for i in range(len(P)):
        for j in range(len(T)):
            
            # Use the result from the previous solution as the initial estimate, if it exists and if it converged.
            if previous_solution and previous_solution.success:
                init = previous_solution.x
            
            # Perform the optimization.
            sol = minimize(gibbs, init, args=(T[j], P[i]),bounds= bnds, method='trust-constr', constraints=cons, options={'disp': False, 'maxiter': 100})


            result.append(sol.x)
            pressure.append(P[i])
            temperature.append(T[j])

    results = pd.DataFrame(result, columns=df.index)
    results['Temperature (K)'] = temperature
    results['Pressure (bar)'] = pressure

    return results