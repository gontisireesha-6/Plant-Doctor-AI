from flask import Flask, render_template, request
from PIL import Image
import numpy as np

from model import predict

app = Flask(__name__)

disease_descriptions = {

"Pepper_bell__Bacterial_spot":
"Bacterial Spot is a bacterial disease that causes small dark water-soaked spots on leaves and fruits. Severe infections reduce yield and fruit quality.",

"Pepper_bell___healthy":
"Great! Your bell pepper plant appears healthy. Continue proper irrigation, balanced fertilization, and regular field monitoring to maintain healthy growth.",

"Potato___Early_blight":
"Early Blight is a fungal disease that causes brown target-like spots on older leaves. If left untreated, it reduces photosynthesis and decreases potato yield.",

"Potato___Late_blight":
"Late Blight is a highly destructive disease caused by Phytophthora infestans. It spreads rapidly during cool, humid weather and can destroy entire potato crops.",

"Potato___healthy":
"Your potato plant appears healthy. Continue good agricultural practices, proper irrigation, and regular crop monitoring.",

"Tomato_Bacterial_spot":
"Bacterial Spot causes dark lesions on tomato leaves, stems, and fruits. Warm, humid conditions favor rapid disease development.",

"Tomato_Early_blight":
"Early Blight is a fungal disease that produces brown circular spots with concentric rings on older leaves. Severe infection leads to early leaf drop and reduced yield.",

"Tomato_Late_blight":
"Late Blight is one of the most serious tomato diseases. It causes large dark lesions on leaves and fruits and spreads quickly during cool, wet weather.",

"Tomato_Leaf_Mold":
"Leaf Mold is a fungal disease that mainly affects tomato leaves in humid conditions. Yellow spots develop on the upper surface while olive-green mold appears underneath.",

"Tomato_Septoria_leaf_spot":
"Septoria Leaf Spot produces numerous small circular spots with dark borders on leaves. Heavy infection causes premature leaf fall and reduced fruit production.",

"Tomato_Spider_mites_Two_spotted_spider_mite":
"Two-Spotted Spider Mites are tiny pests that suck plant sap, causing yellow speckling, leaf drying, and reduced plant vigor during hot and dry conditions.",

"Tomato__Target_Spot":
"Target Spot is a fungal disease that forms circular brown lesions with concentric rings on leaves and fruits, reducing tomato quality and yield.",

"Tomato_Tomato_YellowLeaf_Curl_Virus":
"Tomato Yellow Leaf Curl Virus is transmitted by whiteflies. Infected plants show yellow curled leaves, stunted growth, and poor fruit production.",

"Tomato__Tomato_mosaic_virus":
"Tomato Mosaic Virus causes mottled green and yellow leaves, leaf distortion, and reduced fruit quality. It spreads through infected seeds, tools, and plant contact.",

"Tomato_healthy":
"Excellent! Your tomato plant appears healthy. Continue proper nutrition, irrigation, pest monitoring, and field sanitation to maintain healthy crop growth."

}
organic_treatments = {

"Pepper_bell__Bacterial_spot":
"""• Spray 5 ml Neem Oil + 1 litre water + 2 ml liquid soap.
• Spray once every 7 days.
• Remove infected leaves immediately.""",

"Pepper_bell__healthy":
"Maintain regular watering, add compost, and inspect plants weekly.",

"Potato___Early_blight":
"""• Mix 5 ml Neem Oil + 1 litre water.
• Spray every 7 days.
• Remove infected leaves.""",

"Potato___Late_blight":
"""• Spray 10 g Trichoderma powder in 1 litre water.
• Avoid overhead watering.
• Remove infected plants.""",

"Potato___healthy":
"Apply compost regularly and maintain proper field hygiene.",

"Tomato_Bacterial_spot":
"""• Spray 5 ml Neem Oil + 1 litre water.
• Remove infected leaves.
• Repeat every 7 days.""",

"Tomato_Early_blight":
"""• Spray 5 ml Neem Oil + 1 litre water.
• Add Trichoderma to the soil.
• Repeat every 7 days.""",

"Tomato_Late_blight":
"""• Spray Trichoderma solution.
• Improve air circulation.
• Remove infected leaves.""",

"Tomato_Leaf_Mold":
"""• Reduce humidity.
• Spray Neem Oil every week.""",

"Tomato_Septoria_leaf_spot":
"""• Remove infected leaves.
• Spray Neem Oil every 7 days.""",

"Tomato_Spider_mites_Two_spotted_spider_mite":
"""• Spray 5 ml Neem Oil + 1 litre water.
• Spray on both sides of leaves.""",

"Tomato__Target_Spot":
"""• Spray Neem Oil every week.
• Remove infected leaves.""",

"Tomato_Tomato_YellowLeaf_Curl_Virus":
"""• Control whiteflies using yellow sticky traps.
• Spray Neem Oil weekly.""",

"Tomato__Tomato_mosaic_virus":
"""• Remove infected plants immediately.
• Disinfect tools after use.""",

"Tomato_healthy":
"Continue good irrigation, compost application, and crop monitoring."

}
chemical_treatments = {

"Pepper_bell__Bacterial_spot":
"Use a recommended copper-based bactericide according to the product label. Spray at the first sign of disease and repeat at the interval specified on the label if needed. Remove severely infected plant parts and avoid spraying during the hottest part of the day.",

"Pepper_bell__healthy":
"No chemical treatment is required. Continue regular crop monitoring and good field sanitation.",

"Potato___Early_blight":
"Use a fungicide labeled for Early Blight and apply according to the manufacturer's directions. Begin treatment when symptoms first appear and repeat only as directed on the product label.",

"Potato___Late_blight":
"Apply a fungicide labeled for Late Blight immediately after symptoms are detected or when disease risk is high. Follow all label instructions for timing and application intervals.",

"Potato___healthy":
"No chemical treatment is needed. Maintain preventive crop management practices.",

"Tomato_Bacterial_spot":
"Use a copper-based bactericide registered for tomatoes according to the label. Start spraying early and continue only at the recommended intervals.",

"Tomato_Early_blight":
"Use a fungicide labeled for tomato Early Blight. Follow the product label for dosage, spray timing, and safety precautions.",

"Tomato_Late_blight":
"Apply a fungicide labeled for Late Blight as soon as symptoms appear or when disease pressure is high. Always follow the product label.",

"Tomato_Leaf_Mold":
"Use a fungicide registered for Leaf Mold and improve air circulation in the crop. Apply only according to label instructions.",

"Tomato_Septoria_leaf_spot":
"Apply a fungicide labeled for Septoria Leaf Spot. Remove heavily infected leaves and follow the recommended spray schedule on the label.",

"Tomato_Spider_mites_Two_spotted_spider_mite":
"Use a miticide labeled for spider mites if needed. Rotate products with different modes of action and follow the label carefully.",

"Tomato__Target_Spot":
"Use a fungicide registered for Target Spot and follow the manufacturer's instructions for timing and application frequency.",

"Tomato_Tomato_YellowLeaf_Curl_Virus":
"There is no chemical cure for this virus. Control whiteflies using insecticides labeled for whitefly management and remove infected plants to reduce spread.",

"Tomato__Tomato_mosaic_virus":
"There is no chemical cure for Tomato Mosaic Virus. Remove infected plants, disinfect tools, and follow good sanitation practices.",

"Tomato_healthy":
"No chemical treatment is required. Continue routine monitoring and preventive care."

}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict_image():

    if "file" not in request.files:
        return "No file uploaded"

    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    image = Image.open(file).convert("RGB")
    image = image.resize((256, 256))

    img_array = np.array(image)

    predicted_class, confidence = predict(img_array)

    healthy_plants = [
        "Pepper_bell___healthy",
        "Potato___healthy",
        "Tomato_healthy"
    ]

    is_healthy = predicted_class in healthy_plants

    return render_template(
        "index.html",
        prediction=predicted_class,
        confidence=confidence,
        description=disease_descriptions.get(
            predicted_class,
            "No description available."
        ),
        organic_treatment=organic_treatments.get(
            predicted_class,
            "No organic treatment available."
        ),
        chemical_treatment=chemical_treatments.get(
            predicted_class,
            "No chemical treatment available."
        ),
        is_healthy=is_healthy
    )


if __name__ == "__main__":
    app.run(debug=True)