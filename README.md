# Bitcoin Mining Simulation

This project simulates the process of Bitcoin mining. It includes features such as parallel mining with multiple workers, dynamic difficulty adjustment, block reward halving, and a Flask web interface for monitoring the mining process.

## Features

- **Parallel Mining**: Utilize multiple CPU cores to speed up the mining process.
- **Dynamic Difficulty Adjustment**: Adjusts mining difficulty based on the average mining time.
- **Block Reward Halving**: Halves the mining reward every `HALVING_INTERVAL` blocks.
- **Flask Web Interface**: Provides a web interface to monitor the mining status and start new mining jobs.

## Requirements

- Python 3.7+
- Flask
- tqdm

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/AbdulMuspik/Bitcoin-Miner.git
    cd Bitcoin-Miner
    ```

2. **Install dependencies**:
    ```sh
    pip install flask tqdm
    ```

## Usage

### Command-Line Interface

Run the mining simulation from the command line:

```sh
python main.py [OPTIONS]
```

#### Options:

- `--difficulty`: Set mining difficulty (`Easy`, `Medium`, `Hard`). Default is `Medium`.
- `--block_number`: Block number to mine. Default is `5`.
- `--transactions`: Transactions to include in the block. Default is `"Dhaval->Bhavin->20,Mando->Cara->45"`.
- `--previous_hash`: Previous block's hash. Default is `"0000000xa036944e29568d0cff17edbe038f81208fecf9a66be9a2b8321c6ec7"`.
- `--num_workers`: Number of parallel workers for mining. Default is the number of CPU cores.
- `--config_file`: Path to configuration file for custom block data.
- `--save_file`: File to save the mined block. Default is `"mined_block.json"`.

### Example:

```sh
python main.py --difficulty Medium --block_number 6 --transactions "Alice->Bob->30" --previous_hash "abcd1234" --num_workers 4
```

### Flask Web Interface

Start the Flask web server for monitoring and controlling the mining process:

```sh
python main.py
```

#### Endpoints:

- **GET /status**: Get the current mining status.
- **POST /mine**: Start mining a new block. Example payload:
    ```json
    {
        "difficulty": "Medium",
        "num_workers": 4,
        "transactions": "Alice->Bob->30",
    }
    ```

## Project Structure

- `main.py`: Main script for the mining simulation.
- `block_data.json` (optional): Configuration file for custom block data.

## Configuration File

You can provide a configuration file with custom block data. The file should be in JSON format and contain the following fields:

```json
{
    "block_number": 5,
    "transactions": "Dhaval->Bhavin->20,Mando->Cara->45",
    "previous_hash": "0000000xa036944e29568d0cff17edbe038f81208fecf9a66be9a2b8321c6ec7"
}
```

## Logging

The script logs information about the mining process, including hash rates, block mining times, and difficulty adjustments. Logs are printed to the console.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/AbdulMuspik/Bitcoin-Miner/blob/main/LICENSE) file for details.
