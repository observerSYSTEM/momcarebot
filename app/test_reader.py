from app.plan_reader import read_care_plan_from_excel, format_plan_for_telegram

plan = read_care_plan_from_excel("data/Mom_Care_Monthly_Support_Plan.xlsx")
print(format_plan_for_telegram(plan))
