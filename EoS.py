import numpy as np


def fug(T, P, eq, n, **components):
    
    P = P*100000 # bar -> Pa

    mole_fractions = n/sum(n)

    # Verificar se o componente é carbono sólido
    if components.keys == 'C':
        return 1  # Coeficiente de fugacidade para o carbono sólido

    if eq == 'ideal':
        res = 1
    else:

        # Propriedades da mistura
        Tc_aux = []
        Pc_aux = []
        omega_aux  = []
        for i in components.keys():
            Tc_aux.append(components[i].get('Tc'))
            Pc_aux.append(components[i].get('Pc')*100000)  # bar -> Pa
            omega_aux.append(components[i].get('omega'))

        Tc = np.dot(mole_fractions,Tc_aux)
        Pc = np.dot(mole_fractions,Pc_aux)
        omega = np.dot(mole_fractions,omega_aux)

        R = 8.314  # J/(mol*K)
        
        Tr = T / Tc
        Pr = P / Pc
        
        eos_params = {
            'peng_robinson': {'a': 0.45724, 'b': 0.07780, 'c': 2, 'd': 2},
            'redlich_kwong': {'a': 0.42748, 'b': 0.08664, 'c': 2.0, 'd': 2.5},
            'van_der_waals': {'a': 27/64, 'b': 1/8, 'c': 1, 'd': 1},
            'soave_redlich_kwong': {'a': 0.42748, 'b': 0.08664, 'c': 2.0, 'd': 2.5},
            'patel_teja': {'a': 0.45724, 'b': 0.07780, 'c': 2, 'd': 2}
        }
        
        params = eos_params[eq]
        
        a = params['a'] * (R**params['c'] * Tc**params['d']) / Pc
        b = params['b'] * (R * Tc) / Pc
        
        
        if eq == 'peng_robinson':
            kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
            alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
            a_alpha = a * alpha
            b_alpha = b
            
            A = a_alpha * P / (R**params['c'] * T**params['d'])
            B = b_alpha * P / (R * T)
            
            coefficients = [1, -1, A - B - B**2, -A*B]

            Z_roots = np.roots(coefficients)
            Z_vapor = Z_roots[np.isreal(Z_roots) & (Z_roots > 0)].real[0]
            ln_phi = (b_alpha / b) * (Z_vapor - 1) - np.log(Z_vapor - B) + A / (2 * np.sqrt(2) * B) * np.log((Z_vapor + (1 + np.sqrt(2)) * B) / (Z_vapor + (1 - np.sqrt(2)) * B))

            res = np.exp(ln_phi)

        elif eq == 'redlich_kwong':
            alpha = (1 + 0.401 * omega)
                
            a_alpha = a * alpha
            b_alpha = b
            
            A = a_alpha * P / (R**params['c'] * T**params['d'])
            B = b_alpha * P / (R * T)
            
            coefficients = [1, -1, A - B - B**2, -A*B]

            Z_roots = np.roots(coefficients)
            Z_vapor = Z_roots[np.isreal(Z_roots) & (Z_roots > 0)].real[0]
            ln_phi = (b_alpha / b) * (Z_vapor - 1) - np.log(Z_vapor - B) + A / (2 * np.sqrt(2) * B) * np.log((Z_vapor + (1 + np.sqrt(2)) * B) / (Z_vapor + (1 - np.sqrt(2)) * B))


        elif eq == 'van_der_waals':
            A = a * P / (R * T**2)
            B = b * P / (R * T)
            coefficients = [1, -1 + B, A - 3*B**2, -A*B + B**2 + B**3]
            Z_roots = np.roots(coefficients)
            Z_vapor = Z_roots[np.isreal(Z_roots) & (Z_roots > 0)].real[0]
            ln_phi = (b_alpha / b) * (Z_vapor - 1) - np.log(Z_vapor - B) + A / (2 * np.sqrt(2) * B) * np.log((Z_vapor + (1 + np.sqrt(2)) * B) / (Z_vapor + (1 - np.sqrt(2)) * B))


        elif eq == 'soave_redlich_kwong':
            m = 0.48 + 1.574 * omega - 0.176 * omega**2
            alpha = (1 + m * (1 - np.sqrt(Tr)))**2
            a_alpha = a * alpha
            b_alpha = b
            A = a_alpha * P / (R**params['c'] * T**params['d'])
            B = b_alpha * P / (R * T)
            coefficients = [1, -1, A - B - B**2, -A*B]

            Z_roots = np.roots(coefficients)
            Z_vapor = Z_roots[np.isreal(Z_roots) & (Z_roots > 0)].real[0]
            ln_phi = (b_alpha / b) * (Z_vapor - 1) - np.log(Z_vapor - B) + A / (2 * np.sqrt(2) * B) * np.log((Z_vapor + (1 + np.sqrt(2)) * B) / (Z_vapor + (1 - np.sqrt(2)) * B))

        elif eq == 'patel_teja':
            kappa = 1 + (0.3796 + 1.485 * omega - 0.1644 * omega**2 + 0.01667 * omega**3) * (1 - np.sqrt(Tr))
            alpha = kappa**2
            a_alpha = a * alpha
            b_alpha = b
            
            A = a_alpha * P / (R**eos_params['patel_teja']['c'] * T**eos_params['patel_teja']['d'])
            B = b_alpha * P / (R * T)
            coefficients = [1, -(1 - B), (A - 2*B - 3*B**2), -(A*B - B**2 - B**3)]
            Z_roots = np.roots(coefficients)
            Z_vapor = max(Z_roots[np.isreal(Z_roots)])
            
            ln_phi = (b_alpha / b) * (Z_vapor - 1) - np.log(Z_vapor - B) + A / (2.414 * B) * np.log((Z_vapor + 2.414 * B) / (Z_vapor - 0.414 * B))

        res = np.exp(ln_phi)
    return res