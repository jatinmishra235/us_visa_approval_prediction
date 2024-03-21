from flask import Flask, request, render_template, jsonify, url_for

from us_visa.constant import APP_HOST, APP_PORT
from us_visa.pipeline.prediction_pipeline import USvisaData, USvisaClassifier
from us_visa.pipeline.training_pipeline import TrainingPipeline

app = Flask(__name__)

@app.route("/",methods=["POST","GET"])
def predict():
    if request.method == "GET":
        return render_template("usvisa.html")
    else:
        usvisa_data = USvisaData(continent=request.form.get("continent"),
                                 has_job_experience=request.form.get("has_job_experience"),
                                 requires_job_training=request.form.get("requires_job_training"),
                                 no_of_employees=request.form.get("no_of_employees"),
                                 company_age=request.form.get("company_age"),
                                 region_of_employment=request.form.get("region_of_employment"),
                                 prevailing_wage=request.form.get("prevailing_wage"),
                                 unit_of_wage=request.form.get("unit_of_wage"),
                                 full_time_position=request.form.get("full_time_position"),
                                 education_of_employee=request.form.get("education_of_employee")
        )
        usvisa_df = usvisa_data.get_usvisa_data_input_dataframe()
        model_predictor = USvisaClassifier()
        value = model_predictor.predict(usvisa_df)[0]

        status = None
        if value == 1:
            status = "visa-approved"
        else:
            status = "visa-rejected"

        return render_template("usvisa.html",context=status)
    
@app.get("/train")
def trainRouteClient():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()

        return "training successful !!"
    except Exception as e:
        return f"error occured: {e}"
    
if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT)
    