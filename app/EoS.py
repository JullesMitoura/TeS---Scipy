import numpy as np

def fug(T, P, eq, n, **components):
    
    P = P * 100000  # bar -> Pa
    mole_fractions = n / sum(n)
    
    # Verificar se o componente é carbono sólido
    if components.keys() == 'C':
        return 1  # Coeficiente de fugacidade para o carbono sólido

    if eq == 'ideal':
        return 1  # Fugacidade ideal para gases
    
    # Propriedades da mistura
    Tc_aux = [components[i]['Tc'] for i in components]
    Pc_aux = [components[i]['Pc'] * 100000 for i in components]  # bar -> Pa
    omega_aux = [components[i]['omega'] for i in components]

    Tc = np.dot(mole_fractions, Tc_aux)
    Pc = np.dot(mole_fractions, Pc_aux)
    omega = np.dot(mole_fractions, omega_aux)
    
    R = 8.314  # J/(mol*K)
    Tr = T / Tc
    Pr = P / Pc
    
    # Parâmetros da equação de estado
    eos_params = {
        'peng_robinson': {'a': 0.45724, 'b': 0.07780, 'c': 2, 'd': 2},
        'redlich_kwong': {'a': 0.42748, 'b': 0.08664, 'c': 2.0, 'd': 2.5},
        'soave_redlich_kwong': {'a': 0.42748, 'b': 0.08664, 'c': 2.0, 'd': 2.5}
    }
    
    if eq not in eos_params:
        raise ValueError(f"Equação de estado {eq} não suportada.")
    
    params = eos_params[eq]
    
    # Cálculo de a e b
    a = params['a'] * (R**params['c'] * Tc**params['d']) / Pc
    b = params['b'] * (R * Tc) / Pc
    
    # Função auxiliar para cálculo de alpha e Z_vapor
    def calc_alpha_and_Z_vapor(Tr, Pr, eq, omega, a, b, R, T, P):
        if eq == 'peng_robinson':
            kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
            alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
        elif eq == 'redlich_kwong':
            alpha = (1 + 0.401 * omega)
        elif eq == 'soave_redlich_kwong':
            m = 0.48 + 1.574 * omega - 0.176 * omega**2
            alpha = (1 + m * (1 - np.sqrt(Tr)))**2
        else:
            raise ValueError(f"Equação de estado {eq} não suportada.")
        
        a_alpha = a * alpha
        b_alpha = b
        
        A = a_alpha * P / (R**params['c'] * T**params['d'])
        B = b_alpha * P / (R * T)
        
        coefficients = [1, -1, A - B - B**2, -A * B]
        Z_roots = np.roots(coefficients)
        Z_vapor = Z_roots[np.isreal(Z_roots) & (Z_roots > 0)].real[0]
        
        return alpha, Z_vapor, b_alpha, B, A
    
    # Cálculo de alpha, Z_vapor e outros parâmetros
    alpha, Z_vapor, b_alpha, B, A = calc_alpha_and_Z_vapor(Tr, Pr, eq, omega, a, b, R, T, P)
    
    # Cálculo do ln_phi e da fugacidade
    ln_phi = (b_alpha / b) * (Z_vapor - 1) - np.log(Z_vapor - B) + A / (2 * np.sqrt(2) * B) * np.log((Z_vapor + (1 + np.sqrt(2)) * B) / (Z_vapor + (1 - np.sqrt(2)) * B))
    phi = np.exp(ln_phi)
    
    return phi