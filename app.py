def prediksi(data_input):
    """
    Fungsi prediksi utama untuk dashboard.
    Menggunakan logika Hybrid v5: 70% Akurasi (SMOTETomek) + 30% Sensitivitas (BRF)
    ditambah dengan Kalibrasi Probabilitas untuk deteksi risiko tinggi.
    """
    data = pd.DataFrame([data_input])

    # 1. Preprocessing Teks
    for col in data.select_dtypes(include='object').columns:
        data[col] = data[col].astype(str).str.lower().str.strip()

    # 2. Encoding
    data_enc = pd.get_dummies(data)
    data_enc = data_enc.reindex(columns=fitur_model, fill_value=0)

    # 3. Ambil Probabilitas dari kedua model utama
    # model_smote (Akurasi) & model (Sensitivitas/BRF)
    p_acc = model_smote.predict_proba(data_enc)[0]
    p_sen = model.predict_proba(data_enc)[0]

    # 4. Gabungkan (70/30 Split)
    p_comb = (p_acc * 0.70) + (p_sen * 0.30)

    # 5. Kalibrasi Stabilized v5 (Boost Minoritas)
    # Indeks: 0=Berat, 1=Fatal, 2=Ringan
    p_boosted = np.array([
        p_comb[0] * 1.3, # Boost Berat
        p_comb[1] * 2.0, # Boost Fatal
        p_comb[2] * 1.1  # Stabilisasi Ringan
    ])

    # 6. Normalisasi kembali ke total 100%
    p_final = p_boosted / np.sum(p_boosted)

    return dict(zip(model_smote.classes_, p_final)
)widgets_dict = {}

for col in X.columns:
    if df[col].dtype == 'object':
        widgets_dict[col] = widgets.Dropdown(
            options=sorted(df[col].dropna().unique()),
            description=col[:10]
        )
    else:
        widgets_dict[col] = widgets.IntSlider(
            min=int(df[col].min()),
            max=int(df[col].max()),
            value=int(df[col].median()),
            description=col[:10]
        )
    ef run_prediksi(**input_data):
    hasil = prediksi(input_data)

    print("\n=== HASIL PREDIKSI ===")
    for k, v in hasil.items():
        print(f"{k}: {round(v*100,2)}%")

    # chart data
    data_chart = [
        {"kategori": k, "prob": v}
        for k, v in hasil.items()
    ]

    display(data_chart)
  # @title Default title text
from IPython.display import clear_output, display, HTML
import ipywidgets as widgets
import matplotlib.pyplot as plt
import pandas as pd

# 1. Enhanced UI Styling with Bright Yellow Theme
display(HTML("""
<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'>
<style>
    .main-container { font-family: 'Segoe UI', Tahoma, sans-serif; }
    .corporate-header {
        background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
        color: #2c3e50; padding: 30px; border-radius: 20px; text-align: center;
        margin-bottom: 20px; box-shadow: 0 10px 20px rgba(243, 156, 18, 0.2);
        border: 2px solid #f39c12;
    }
    .prediction-card {
        background: #ffffff; border-left: 8px solid #f1c40f;
        padding: 20px; border-radius: 10px; margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .widget-label { font-weight: 600; color: #2c3e50; }
</style>
<div class='main-container'>
    <div class='corporate-header'>
        <h1 style='margin:0;'><i class='fa-solid fa-triangle-exclamation'></i> Accident Risk Predictor</h1>
        <p style='font-weight: bold; opacity: 0.9;'>Estimasi Tingkat Keparahan Kecelakaan Kab. Gresik</p>
    </div>
</div>
"""))

if 'X_encoded' in globals():
    icon_map = {
        'direction': 'fa-compass', 'tipe cahaya': 'fa-sun', 'cuaca': 'fa-cloud-sun',
        'fungsi jalan': 'fa-road', 'kelas jalan': 'fa-layer-group', 'geometri jalan': 'fa-bezier-curve',
        'tipe jalan': 'fa-arrows-split-up-and-left', 'kecepatan': 'fa-gauge-high', 'jenis jalan': 'fa-map-location-dot',
        'kecamatan': 'fa-city', 'age': 'fa-id-card', 'jenis kelamin': 'fa-venus-mars',
        'jenis kendaraan': 'fa-car-side', 'atribut_keselamatan': 'fa-user-shield', 'kepemilikan_sim': 'fa-address-card'
    }

    widgets_dict = {}
    style = {'description_width': 'initial'}
    layout = widgets.Layout(width='100%', margin='5px 0')

    for col in selected_features:
        icon = icon_map.get(col, 'fa-list')
        label_html = f"<i class='fa-solid {icon}' style='color:#f39c12; width:25px;'></i> <span class='widget-label'>{col.title()}</span>"

        if df[col].dtype == 'object':
            w = widgets.Dropdown(options=sorted(df[col].unique()), style=style, layout=layout)
        else:
            w = widgets.IntSlider(min=int(df[col].min()), max=int(df[col].max()), value=int(df[col].median()), style=style, layout=layout)

        widgets_dict[col] = widgets.VBox([widgets.HTML(label_html), w])

    items = list(widgets_dict.values())
    form_ui = widgets.HBox([
        widgets.VBox(items[:7], layout=widgets.Layout(width='48%')),
        widgets.VBox(items[7:], layout=widgets.Layout(width='48%'))
    ])

    btn_predict = widgets.Button(description='PROSES ESTIMASI RISIKO', button_style='warning', icon='bolt', layout=widgets.Layout(width='100%', height='50px', margin='20px 0'))
    output_result = widgets.Output()

    def handle_prediction(b):
        with output_result:
            clear_output(wait=True)
            input_values = {col: vb.children[1].value for col, vb in widgets_dict.items()}
            res = prediksi(input_values)

            display(HTML("<div class='prediction-card'><h3><i class='fa-solid fa-chart-pie'></i> Pie Chart Estimasi Risiko:</h3></div>"))

            fig, ax = plt.subplots(figsize=(7, 7))
            colors = ['#f39c12', '#e74c3c', '#27ae60'] # Orange (Berat), Red (Fatal), Green (Ringan)

            categories = ['kecelakaan berat', 'kecelakaan fatal', 'kecelakaan ringan']
            values = [res.get(cat, 0) for cat in categories]
            labels = [cat.upper() for cat in categories]

            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                              startangle=140, colors=colors, explode=(0.05, 0.05, 0.05),
                                              shadow=True, textprops={'fontweight': 'bold'})

            plt.setp(autotexts, size=11, color="white")
            plt.title('Estimasi Risiko Tingkat Keparahan LAKA di Gresik', fontsize=14, pad=20, fontweight='bold')
            plt.show()

    btn_predict.on_click(handle_prediction)
    display(form_ui, btn_predict, output_result)
else:
    print("Data belum siap. Jalankan cell encoding sebelumnya.")
