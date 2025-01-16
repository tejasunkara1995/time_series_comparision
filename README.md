
## Usage

### Basic Usage

```python
from time_series_comparison import run_analysis

run_analysis(
    input_file="path/to/your/file.xlsx",
    db_url="postgresql://username:password@localhost/database_name",
    output_dir="output_data",
    input_date_column="Week Ending Date",
    input_value_column="Detections",
    db_date_column="Date",
    db_value_column="Value",
    num_plots=5
)
```

### Parameters

- `input_file`: Path to your input Excel/CSV file
- `db_url`: PostgreSQL database connection URL
- `output_dir`: Directory for output files (default: "output_data")
- `input_date_column`: Date column name in input file (default: "Week Ending Date")
- `input_value_column`: Value column name in input file (default: "Detections")
- `db_date_column`: Date column name in database (default: "Date")
- `db_value_column`: Value column name in database (default: "Value")
- `num_plots`: Number of comparison plots to generate (default: 5)

### Input File Format

Your input file should contain at least two columns:
- A date column (e.g., "Week Ending Date")
- A value column (e.g., "Detections")

Example Excel/CSV format:
```
Week Ending Date | Detections
2023-01-01      | 123
2023-01-08      | 456
...
```

### Database Table Format

Database tables should contain:
- A date column (e.g., "Date")
- A value column (e.g., "Value")

## Output

The tool generates:
1. Normalized data files (CSV)
2. Similarity scores (CSV)
3. Comparison plots (PNG)

Output files are organized in the specified output directory:
```
output_data/
├── normalized_input.csv
├── similarity_results.csv
├── comparison_table1.png
├── comparison_table2.png
└── ...
```

## Example Code

```python
# Configure database connection
db_config = {
    'username': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'your_database'
}

# Create database URL
db_url = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"

# Run analysis
run_analysis(
    input_file="data/input/timeseries_data.xlsx",
    db_url=db_url,
    output_dir="data/output",
    input_date_column="Week Ending Date",
    input_value_column="Detections",
    db_date_column="Date",
    db_value_column="Value"
)
```
