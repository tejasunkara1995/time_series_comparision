import os
import pandas as pd
import matplotlib.pyplot as plt 
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def process_input_file(file_path, output_dir, date_column='Week Ending Date', value_column='Detections'):
    """
    Process and normalize input file data.
    
    Parameters:
        file_path (str): Path to input Excel/CSV file
        output_dir (str): Output directory for normalized data
        date_column (str): Name of the date column in input file
        value_column (str): Name of the value column to normalize
        
    Returns:
        tuple: (pd.DataFrame, str) - Normalized input data and the value column name
    """
    print(f"Processing input file: {file_path}")
    
    # Read input file based on extension
    if file_path.endswith(('.xlsx', '.xls')):
        data = pd.read_excel(file_path)
    else:
        data = pd.read_csv(file_path)
    
    # Validate columns exist
    if date_column not in data.columns:
        raise ValueError(f"Date column '{date_column}' not found in input file")
    if value_column not in data.columns:
        raise ValueError(f"Value column '{value_column}' not found in input file")
    
    # Process dates and set index
    data[date_column] = pd.to_datetime(data[date_column])
    data.set_index(date_column, inplace=True)
    
    # Normalize data
    scaler = StandardScaler()
    normalized_data = pd.DataFrame(
        scaler.fit_transform(data[[value_column]]),
        columns=[value_column],
        index=data.index
    )
    
    # Save normalized data
    output_path = os.path.join(output_dir, 'normalized_input.csv')
    normalized_data.to_csv(output_path)
    print(f"Normalized input saved to: {output_path}")
    
    return normalized_data, value_column

def process_database_table(engine, table_name, output_dir, db_date_column='Date', db_value_column='Value'):
    """
    Process and normalize a single database table.
    
    Parameters:
        engine: SQLAlchemy engine
        table_name (str): Name of the table to process
        output_dir (str): Output directory for normalized data
        db_date_column (str): Name of the date column in database
        db_value_column (str): Name of the value column in database
        
    Returns:
        tuple: (table_name, normalized_data) or None if error
    """
    try:
        # Read table data
        query = f'SELECT * FROM "{table_name}"'
        data = pd.read_sql(query, engine, parse_dates=[db_date_column])
        
        # Validate columns exist
        if db_date_column not in data.columns:
            print(f"Date column '{db_date_column}' not found in table {table_name}")
            return None
        if db_value_column not in data.columns:
            print(f"Value column '{db_value_column}' not found in table {table_name}")
            return None
            
        data.set_index(db_date_column, inplace=True)
        
        # Normalize table data
        scaler = StandardScaler()
        normalized_data = pd.DataFrame(
            scaler.fit_transform(data[[db_value_column]]),
            columns=[db_value_column],
            index=data.index
        )
        
        # Save normalized table
        output_path = os.path.join(output_dir, f'{table_name}_normalized.csv')
        normalized_data.to_csv(output_path)
        
        return (table_name, normalized_data)
        
    except Exception as e:
        print(f"Error processing table {table_name}: {e}")
        return None

def calculate_similarity(input_series, table_series):
    """
    Calculate cosine similarity between two series.
    
    Parameters:
        input_series: Input data series
        table_series: Table data series
        
    Returns:
        float: Similarity score
    """
    return cosine_similarity(
        input_series.values.reshape(1, -1),
        table_series.values.reshape(1, -1)
    )[0][0]

def process_database(db_url, input_data, value_column, output_dir, 
                    db_date_column='Date', db_value_column='Value'):
    """
    Process database tables and calculate similarities.
    
    Parameters:
        db_url (str): Database connection URL
        input_data (pd.DataFrame): Normalized input data
        value_column (str): Name of the value column from input data
        output_dir (str): Output directory for results
        db_date_column (str): Name of the date column in database
        db_value_column (str): Name of the value column in database
        
    Returns:
        pd.DataFrame: Similarity results
    """
    print("\nProcessing database tables...")
    engine = create_engine(db_url)
    
    # Get list of tables
    tables = pd.read_sql_query(
        "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'",
        engine
    )
    
    # Process each table and calculate similarities
    similarities = []
    for table_name in tables['tablename']:
        result = process_database_table(
            engine, table_name, output_dir, 
            db_date_column, db_value_column
        )
        
        if result:
            table_name, normalized_data = result
            similarity = calculate_similarity(
                input_data[value_column],
                normalized_data[db_value_column]
            )
            
            similarities.append({
                'Table': table_name,
                'Similarity': similarity
            })
            print(f"Processed {table_name}: Similarity = {similarity:.4f}")
    
    # Create and save results DataFrame
    results_df = pd.DataFrame(similarities)
    results_df = results_df.sort_values('Similarity', ascending=False)
    results_df.to_csv(os.path.join(output_dir, 'similarity_results.csv'), 
                     index=False)
    
    return results_df



def visualize_results(similarity_results, normalized_input, input_value_column, 
                     normalized_dir, num_plots=5):
    """
    Create visualization plots comparing top similar tables with input data.
    
    Parameters:
        similarity_results (pd.DataFrame): DataFrame with similarity scores
        normalized_input (pd.DataFrame): Normalized input data
        input_value_column (str): Name of the value column in input data
        normalized_dir (str): Directory containing normalized table files
        num_plots (int): Number of top tables to plot
    """
    # Get top N similar tables
    top_tables = similarity_results.nlargest(num_plots, "Similarity")
    
    # Create plots for each top table
    for _, row in top_tables.iterrows():
        table_name = row["Table"]
        similarity = row["Similarity"]
        
        try:
            # Load the normalized table data
            table_path = os.path.join(normalized_dir, f"{table_name}_normalized.csv")
            normalized_table = pd.read_csv(table_path, index_col="Date", parse_dates=True)
            
            # Create the plot
            plt.figure(figsize=(12, 6))
            
            # Plot both series
            plt.plot(normalized_table.index, normalized_table["Value"], 
                    label=f"Table: {table_name}", linewidth=2)
            plt.plot(normalized_input.index, normalized_input[input_value_column], 
                    label="Input Data", linestyle="--", linewidth=2)
            
            # Customize the plot
            plt.title(f"Time Series Comparison: {table_name}\nCosine Similarity: {similarity:.4f}", 
                     fontsize=14, pad=20)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Normalized Value", fontsize=12)
            plt.legend(fontsize=10)
            plt.grid(True, alpha=0.3)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save the plot
            plot_path = os.path.join(normalized_dir, f"comparison_{table_name}.png")
            plt.savefig(plot_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            print(f"Created comparison plot for {table_name}")
            
        except Exception as e:
            print(f"Error creating plot for {table_name}: {e}")

def run_analysis(input_file, db_url, output_dir="output_data", 
                input_date_column='Week Ending Date', 
                input_value_column='Detections',
                db_date_column='Date',
                db_value_column='Value',
                num_plots=5):
    """
    Main function to run the complete analysis pipeline.
    
    Parameters:
        input_file (str): Path to input file
        db_url (str): Database connection URL
        output_dir (str): Output directory
        input_date_column (str): Name of the date column in input file
        input_value_column (str): Name of the value column in input file
        db_date_column (str): Name of the date column in database
        db_value_column (str): Name of the value column in database
        num_plots (int): Number of top similar tables to plot
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process input file
        input_data, value_column = process_input_file(
            input_file, output_dir, 
            input_date_column, input_value_column
        )
        
        # Process database and get results
        results = process_database(
            db_url, input_data, value_column, output_dir,
            db_date_column, db_value_column
        )
        
        # Display top results
        print(f"\nTop {num_plots} most similar tables:")
        print(results.head(num_plots))
        
        # Create visualization plots
        print("\nGenerating comparison plots...")
        visualize_results(
            results, input_data, value_column, 
            output_dir, num_plots
        )
        print(f"\nPlots have been saved in: {output_dir}")
        
    except Exception as e:
        print(f"Error in analysis: {e}")

# Example usage
if __name__ == "__main__":
    # Configuration
    input_file = "path/to/your/input_file.xlsx"
    database_url = "postgresql://username:password@localhost/database_name"
    output_directory = "processed_data"
    
    # Run the analysis with custom column names and visualization
    run_analysis(
        input_file=input_file,
        db_url=database_url,
        output_dir=output_directory,
        input_date_column='Week Ending Date',  # Customize input file date column
        input_value_column='Detections',       # Customize input file value column
        db_date_column='Date',                 # Customize database date column
        db_value_column='Value',               # Customize database value column
        num_plots=5                            # Number of plots to generate
    )