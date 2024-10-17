import matplotlib.pyplot as plt

def line_graf(data,var):
    P = data['Pressure (bar)'].unique()
    font = {'size': 10}
    plt.rc('font', **font)
    fig, axs = plt.subplots()

    for i in P:
        axs.plot(data['Temperature (K)'][data['Pressure (bar)']==i], data[var][data['Pressure (bar)']==i], label = f'{i:.2f} bar')
    
    plt.ylabel(f'{var} (mols)')
    plt.xlabel('Temperature (K)')
    plt.legend(bbox_to_anchor=(1,1), loc="upper left", fontsize=8, frameon=False)
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def line_graf_T(data,var):
    T = data['Temperature (K)'].unique()
    font = {'size': 10}
    plt.rc('font', **font)
    fig, axs = plt.subplots()

    for i in T:
        axs.plot(data['Pressure (bar)'][data['Temperature (K)']==i], data[var][data['Temperature (K)']==i], label = f'{i:.2f} K')
    
    plt.ylabel(f'{var} (mols)')
    plt.xlabel('Pressure (bar)')
    plt.legend(bbox_to_anchor=(1,1), loc="upper left", fontsize=8, frameon=False)
    plt.tight_layout()
    plt.grid(True)
    plt.show()