from time_series_comparision import run_analysis 
run_analysis(
    input_file="/Users/tejasunkara/Projects/MastersProject/webscrapping/Data_Extraction_files/Adenovirus/Adenovirus_Region 1.xlsx",
    db_url="postgresql://postgres:tejacherry@localhost/NREVSS_Database",
    output_dir="output_data",
    input_value_column="Detections",  # Customize for your input file
    num_plots=5 
)