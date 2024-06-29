### importing
import pandas as pd
import numpy as np
import plotly.express as px
import kaleido
import plotly.graph_objects as go
import jalali_pandas
from PIL import Image
import io


### sunburst plots
my_font = dict(
        family="Vazir FD-WOL", # TODO: read font from disk: fonts diretory
        size=10,
        color="black" # TODO: if possible rename isBoy column names here only
    )

df = pd.read_csv("ntickets.csv")
df.loc[df['UniversityName'].str.contains("اقبال", na=False), "UniversityName"] = "دانشگاه اقبال لاهوری مشهد"
df.loc[df['UniversityName'].str.contains("فرهنگیان", na=False), "UniversityName"] = "دانشگاه فرهنگیان مشهد"
df.loc[df['UniversityName'].str.contains("آزاد", na=False), "UniversityName"] = "دانشگاه آزاد مشهد"
isboy = px.pie(df, names="IsBoy") # TODO: pep8
df["Sex"] = df.apply(lambda row: "پسر" if row["IsBoy"] else "دختر", axis=1)
fumfaculty = px.pie(df, names="FumFaculty") # TODO: pep8
df.fillna({"UniversityName": "غیر دانشجو"}, inplace=True)
fig = fig = px.sunburst(df, path=["Sex","UniversityName"], color_discrete_sequence=["tomato","orchid"])
fig.update_layout(
    title="دانشگاه‌های مربوط به شرکت‌کنندگان",
    title_x=0.5,
    showlegend=True,
    font= my_font,
    margin=dict(l=0, r=0, t=30, b=0)
                )
fig.update_traces(textfont_size=20)

unies_bytes = fig.to_image(format="png", width=400, height=400)
# instead of writing on disk, write it as byte buffer on memory and then read it later
# More: https://pillow.readthedocs.io/en/stable/reference/Image.html


### EntranceYear
sunburst_df = df.copy()
sunburst_df = sunburst_df[sunburst_df["IsFumStudent"] == True] # TODO: use column "isFumStudent" to filter instead
sunburst_df["EntranceYear"] = np.where(sunburst_df["EntranceYear"] < 1400,
                                       abs(sunburst_df["EntranceYear"]) % 100,
                                       abs(sunburst_df["EntranceYear"]) % 1000)
sunburst_df["EntranceYear"] = sunburst_df["EntranceYear"].astype(int)
fig = px.sunburst(sunburst_df, path=["Sex","FumFaculty", "EntranceYear"], color_discrete_sequence=["darkorchid","crimson"])
fig.update_layout(
    title="دانشکده‌های مربوط به دانشجویان دانشگاه فردوسی",
    title_x=0.5,
    font=my_font,
    margin=dict(l=0, r=0, t=30, b=9)
                )
fig.update_traces(insidetextorientation='horizontal', textfont_size=8)
fig.update_layout(uniformtext_minsize=5)
entranceyear_bytes = fig.to_image(format="png", width=400, height=400)

### bar charts
population = {"مهندسی" : 6425,
             "منابع طبیعی و محیط زیست" : 530, 
             "معماری و شهرسازی" : 370,
             "کشاورزی": 2675,
             "علوم ورزشی" : 835,
             "علوم ریاضی" : 1335,
             "علوم تربیتی و روانشناسی": 1660,
             "علوم اداری و اقتصادی" : 2510,
             "علوم" : 2355,
             "دامپزشکی" : 900,
             "حقوق و علوم سیاسی" : 1505,
             "الهیات و معارف اسلامی" : 1555,
             "ادبیات و علوم انسانی" : 3550}

faculty_counts = df["FumFaculty"].value_counts().to_dict()
interest_ratios = {fac: faculty_counts.get(fac, 0) / pop for fac, pop in population.items()}
max_interest = max(interest_ratios.values())
normalized_interest_ratios = {fac: interest / max_interest for fac, interest in interest_ratios.items()}
updated_population = {fac: {"name": fac, "interest": normalized_interest_ratios[fac]} for fac in population.keys()}
interest_df = pd.DataFrame.from_dict(updated_population, orient='index').reset_index(drop=True)

fig = px.bar(interest_df, x= "name", y= "interest", color= "name")
fig.update_layout(
    title="میزان علاقه‌مندی دانشکده‌های مختلف فردوسی بر اساس مشارکت و جمعیت کل",
    title_x=0.5,
    xaxis_title="دانشکده",
    yaxis_title="علاقه‌مندی",
    showlegend=False,
    font= my_font,
    margin=dict(l=30, r=0, t=30, b=30)
                )
fig.update_traces(marker_line_color = "black", marker_line_width = 0.3)
facultyinterest_bytes = fig.to_image(format="png", width=1000, height=550)


### Date
df["PurchaseTime"] = pd.to_datetime(df["PurchaseTime"]).dt.tz_localize(None) 
df["MyZonePurchaseTime"] = df["PurchaseTime"] + pd.Timedelta("03:30:00")
df["Hour"] = df["MyZonePurchaseTime"].dt.hour 
df["Date"] = df["MyZonePurchaseTime"].dt.date 
df["JalaliDate"] = df.Date.jalali.to_jalali()
date_df = df.groupby("JalaliDate").size().reset_index(name="Count")
hour_df = df.groupby("Hour").size().reset_index(name="Count")

hourfig = px.line(hour_df, x="Hour", y="Count", color_discrete_sequence=["blue"])
hourfig.update_layout(
    title="میزان خرید بلیت بر اساس ساعت",
    title_x=0.5,
    xaxis_title="ساعت",
    yaxis_title="تعداد",
    font= my_font,
    margin=dict(l=30, r=0, t=30, b=30))
datefig = px.line(date_df, x="JalaliDate", y="Count", color_discrete_sequence=["red"])
datefig.update_layout(
        xaxis=dict(
        tickformat="%y/%m/%d"
    ),
    title="میزان خرید بلیت بر اساس تاریخ",
    title_x=0.5,
    xaxis_title="تاریخ",
    yaxis_title="تعداد",
    font= my_font,
    margin=dict(l=30, r=0, t=30, b=30))
hour_bytes = hourfig.to_image(format="png", width=1000, height=350)
date_bytes = datefig.to_image(format="png", width=1000, height=350)


### Concat
im1 = Image.open("logo.jpg").resize((100, 100))
im2 = Image.open(io.BytesIO(unies_bytes))
im3 = Image.open(io.BytesIO(entranceyear_bytes))
im4 = Image.open(io.BytesIO(facultyinterest_bytes))
im5 = Image.open(io.BytesIO(hour_bytes))
im6 = Image.open(io.BytesIO(date_bytes))
def get_concat_v():
    dst = Image.new("RGB", (1080,1920), (255, 255, 255))
    dst.paste(im2, (70, 120))
    dst.paste(im1, (10, 10))
    dst.paste(im3, (im2.width+210, 120))
    dst.paste(im4, (40, im2.height+200))
    dst.paste(im5, (40, im2.height+im4.height+250))
    dst.paste(im6, (40, im2.height+im4.height+575))
    return dst
    
get_concat_v().save("concat.png")
