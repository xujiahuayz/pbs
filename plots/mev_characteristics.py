import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from concurrent.futures import ProcessPoolExecutor, as_completed
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter

def process_file(file):
    try:
        filename = os.path.basename(file)
        params = filename.split('=')[1:]
        mev_builders = int(params[0].split('characteristic')[0])
        characteristic = float(params[1].replace('.csv', ''))
        
        df = pd.read_csv(file)
        
        df['mev_builders'] = mev_builders
        df['characteristic'] = characteristic
        df['total_block_value'] = df['gas_captured'] + df['mev_captured']
        df['reward'] = df['gas_captured'] + df['mev_captured'] - df['block_bid']
        
        return df
    except Exception as e:
        print(f"Error processing file {file}: {e}")
        return pd.DataFrame() 
    
def process_files_in_batches(files, dataframes):
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_file, file): file for file in files}
        for future in as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                if not result.empty:
                    dataframes.append(result)
            except Exception as e:
                print(f"Error with file {file}: {e}")

def create_meshgrid_interpolated(data, value, sigma=2):
    x = data['mev_builders']
    y = data['characteristic']
    z = data[value]

    xi = np.linspace(x.min(), x.max(), 100)
    yi = np.linspace(y.min(), y.max(), 100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((x, y), z, (xi, yi), method='cubic')
    zi = gaussian_filter(zi, sigma=sigma)

    return xi, yi, zi

def create_3d_plot(x, y, z, xlabel, ylabel, zlabel, title, filename=None):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(x, y, z, cmap='viridis', alpha=0.8)
    ax.set_xlabel(xlabel, labelpad=20)
    ax.set_ylabel(ylabel, labelpad=20)
    ax.set_zlabel(zlabel, labelpad=20)
    ax.set_title(title, pad=20)
    fig.tight_layout(rect=[0, 0, 1, 1])
    plt.subplots_adjust(left=0.2, right=0.8, top=0.85, bottom=0.2)
    if filename:
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.5, dpi=300)
    plt.close(fig)

def plot_total_block_value(grouped_data, save_dir):
    x, y, z = create_meshgrid_interpolated(grouped_data, 'total_block_value')
    create_3d_plot(x, y, z, 'MEV Builders', 'Characteristic', 'Total Block Value', 
                   'Total Block Value vs. MEV Builders and Characteristic', 
                   os.path.join(save_dir, 'total_block_value.png'))

def plot_block_bid(grouped_data, save_dir):
    x, y, z = create_meshgrid_interpolated(grouped_data, 'block_bid')
    create_3d_plot(x, y, z, 'MEV Builders', 'Characteristic', 'Winning Block Bid', 
                   'Winning Block Bid vs. MEV Builders and Characteristic', 
                   os.path.join(save_dir, 'block_bid.png'))

def plot_gas_captured(grouped_data, save_dir):
    x, y, z = create_meshgrid_interpolated(grouped_data, 'gas_captured')
    create_3d_plot(x, y, z, 'MEV Builders', 'Characteristic', 'Gas Captured', 
                   'Gas Captured vs. MEV Builders and Characteristic', 
                   os.path.join(save_dir, 'gas_captured.png'))

def plot_mev_captured(grouped_data, save_dir):
    x, y, z = create_meshgrid_interpolated(grouped_data, 'mev_captured')
    create_3d_plot(x, y, z, 'MEV Builders', 'Characteristic', 'MEV Captured', 
                   'MEV Captured vs. MEV Builders and Characteristic', 
                   os.path.join(save_dir, 'mev_captured.png'))

def plot_reward(grouped_data, save_dir):
    x, y, z = create_meshgrid_interpolated(grouped_data, 'reward')
    create_3d_plot(x, y, z, 'MEV Builders', 'Characteristic', 'Reward', 
                   'Reward vs. MEV Builders and Characteristic', 
                   os.path.join(save_dir, 'reward.png'))

if __name__ == '__main__':
    csv_path = "/Users/tammy/Downloads/vary_mev_and_characteristic"
    save_dir = "./figures"
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    all_files = glob.glob(os.path.join(csv_path, "*.csv"))
    
    dataframes = []
    
    batch_size = 50
    for i in range(0, len(all_files), batch_size):
        batch_files = all_files[i:i + batch_size]
        process_files_in_batches(batch_files, dataframes)
    
    if dataframes:
        all_data = pd.concat(dataframes, ignore_index=True)
    
        grouped_data = all_data.groupby(['mev_builders', 'characteristic']).mean().reset_index()
        
        plot_total_block_value(grouped_data, save_dir)
        plot_block_bid(grouped_data, save_dir)
        plot_gas_captured(grouped_data, save_dir)
        plot_mev_captured(grouped_data, save_dir)
        plot_reward(grouped_data, save_dir)
    else:
        print("No data to plot.")
