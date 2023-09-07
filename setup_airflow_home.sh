# airflow config list --defaults > "${AIRFLOW_HOME}/airflow.cfg"
# https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html
read -p "Enter the folder path (leave empty for default '$(pwd)'): " new_folder
new_folder="${new_folder:-$(pwd)}"

# Escape slashes for sed
new_folder_escaped=$(echo "$new_folder" | sed 's/\//\\\//g')

# Replace the line in the text file
sed -i "s/dags_folder = .*/dags_folder = $new_folder_escaped\/airflow\/dags/" airflow/airflow.cfg
sed -i "s/plugins_folder = .*/plugins_folder = $new_folder_escaped\/airflow\/plugins/" airflow/airflow.cfg
sed -i "s/base_log_folder = .*/base_log_folder = $new_folder_escaped\/airflow\/logs/" airflow/airflow.cfg
sed -i "s/dag_processor_manager_log_location = .*/dag_processor_manager_log_location = $new_folder_escaped\/airflow\/logs\/dag_processor_manager\/dag_processor_manager.log/" airflow/airflow.cfg
sed -i "s/child_process_log_directory = .*/child_process_log_directory = $new_folder_escaped\/airflow\/logs\/scheduler/" airflow/airflow.cfg