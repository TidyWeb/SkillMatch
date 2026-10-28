import io
import pandas as pd
import requests
import yaml

# URLs from the workbook
csv_url = 'https://raw.githubusercontent.com/TidyWeb/SkillMatch/data-snapshots/data/live_snapshots/20261021_2033_reprocessed/skills.csv'
yaml_url = 'https://raw.githubusercontent.com/TidyWeb/SkillMatch/main/John%27s%20Folder/SkillMatch_App_Data/data/taxonomy/technical_skills.yaml'


def get_data_skills():
    # 1. Fresh load of the skills DataFrame
    response_csv = requests.get(csv_url)
    skills_fresh = pd.read_csv(io.StringIO(response_csv.text))

    # 2. Get the top 25 skills by number of distinct vacancies
    top_25_counts = (
        skills_fresh
        .groupby('skill')['vacancy_id']
        .nunique()                      # distinct vacancies per skill
        .sort_values(ascending=False)
        .head(25)
        .reset_index()
    )
    top_25_counts.columns = ['skill', 'count']

    # 2b. Merge in strength + confidence (assumed per skill)
    meta_fields = skills_fresh[['skill', 'strength',
                                'confidence']].drop_duplicates('skill')
    top_25_counts = top_25_counts.merge(meta_fields, on='skill', how='left')

    # 3. Fresh load of the taxonomy to get course coverage
    response_yaml = requests.get(yaml_url)
    taxonomy_data = yaml.safe_load(response_yaml.text)

    rows = []
    for item in taxonomy_data.get("skills", []):
        rows.append({
            "skill": item.get("id"),
            "course_covered": item.get("course_covered", False)
        })
    taxonomy_df = pd.DataFrame(rows)

    # 4. Combine top 25 skills with course coverage
    combined_df = pd.merge(top_25_counts, taxonomy_df, on='skill', how='left')

    return combined_df
