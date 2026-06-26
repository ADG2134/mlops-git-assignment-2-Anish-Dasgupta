"""
Part 3: Data Quality Report

Runs the 'customer_data_expectations' suite against the REAL
data/customer_data.csv, captures validation results, builds Great
Expectations Data Docs (HTML), and computes exact per-issue counts.
"""
import json
import re
import pandas as pd
import great_expectations as gx

PROJECT_ROOT_DIR = "."
CSV_PATH = "data/customer_data.csv"
VALID_COUNTRIES = ["USA", "Canada", "UK", "Australia"]
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def run_validation():
    context = gx.get_context(mode="file", project_root_dir=PROJECT_ROOT_DIR)
    checkpoint = context.checkpoints.get("customer_data_checkpoint")
    result = checkpoint.run()

    context.build_data_docs()
    site_urls = context.get_docs_sites_urls()
    print("Data Docs built. Local site(s):")
    for site in site_urls:
        print(f"  {site['site_name']}: {site['site_url']}")

    return result, context


def summarize_validation(result):
    print("\n" + "=" * 70)
    print("GREAT EXPECTATIONS VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Overall validation success: {result.success}\n")

    for key, validation_result in result.run_results.items():
        stats = validation_result.statistics
        print(f"Total expectations evaluated : {stats['evaluated_expectations']}")
        print(f"Successful expectations       : {stats['successful_expectations']}")
        print(f"Unsuccessful expectations     : {stats['unsuccessful_expectations']}")
        print(f"Success percent                : {stats['success_percent']:.1f}%\n")

        print(f"{'Expectation':45} {'Column':15} {'Result'}")
        print("-" * 75)
        for r in validation_result.results:
            cfg = r.expectation_config
            col = cfg.kwargs.get("column", "-")
            status = "PASS" if r.success else "FAIL"
            unexpected = r.result.get("unexpected_count", "-") if r.result else "-"
            print(f"{cfg.type:45} {col:15} {status:6} unexpected={unexpected}")


def compute_issue_counts():
    """Independent pandas-based audit producing exact counts per issue type."""
    df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
    total = len(df)

    issues = {"total_rows": total}

    # customer_id
    issues["missing_customer_id"] = int((df["customer_id"].str.strip() == "").sum())
    nonblank_ids = df["customer_id"][df["customer_id"].str.strip() != ""]
    issues["duplicate_customer_id_rows"] = int(nonblank_ids.duplicated().sum())
    issues["fully_duplicate_rows"] = int(df.duplicated().sum())

    # age
    age_numeric = pd.to_numeric(df["age"], errors="coerce")
    issues["missing_age"] = int((df["age"].str.strip() == "").sum())
    issues["age_out_of_range"] = int(((age_numeric < 0) | (age_numeric > 120)).sum())

    # email
    issues["missing_email"] = int((df["email"].str.strip() == "").sum())
    nonblank_email = df["email"][df["email"].str.strip() != ""]
    issues["invalid_email_format"] = int(
        (~nonblank_email.apply(lambda x: bool(EMAIL_REGEX.match(x)))).sum()
    )

    # salary
    issues["missing_salary"] = int((df["salary"].str.strip() == "").sum())
    salary_numeric = pd.to_numeric(df["salary"], errors="coerce")
    issues["negative_salary"] = int((salary_numeric < 0).sum())

    # country
    issues["missing_country"] = int((df["country"].str.strip() == "").sum())
    issues["invalid_country"] = int(
        (~df["country"].isin(VALID_COUNTRIES)).sum()
    )

    # phone
    issues["missing_phone"] = int((df["phone"].str.strip() == "").sum())
    nonblank_phone = df["phone"][df["phone"].str.strip() != ""]
    issues["inconsistent_phone_format"] = int(
        (~nonblank_phone.str.match(r"^\d{3}-\d{3}-\d{4}$")).sum()
    )

    # signup_date
    issues["missing_signup_date"] = int((df["signup_date"].str.strip() == "").sum())

    with open("data_quality_issue_counts.json", "w") as f:
        json.dump(issues, f, indent=2)

    print("\n" + "=" * 70)
    print("DATA QUALITY ISSUE COUNTS (independent pandas audit)")
    print("=" * 70)
    for k, v in issues.items():
        pct = f"{(v/total*100):.2f}%" if k != "total_rows" else ""
        print(f"  {k:32}: {v:6} {pct}")

    return issues


if __name__ == "__main__":
    result, context = run_validation()
    summarize_validation(result)
    compute_issue_counts()
