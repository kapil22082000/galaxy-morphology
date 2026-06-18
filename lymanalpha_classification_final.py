#!/usr/bin/env python
# coding: utf-8

# In[2]:


#!/usr/bin/env python
# coding: utf-8

from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row, gridplot
from bokeh.models import (
    Button,
    Select,
    Slider,
    TextInput,
    RadioButtonGroup,
    TextAreaInput,
    Div,
    ColumnDataSource,
    CustomJS
)

from bokeh.palettes import (
    Magma256,
    Inferno256,
    Viridis256,
    Cividis256,
    Greys256
)

import pandas as pd
import numpy as np
import os
import glob

from astropy.io import fits
from astropy.visualization import (
    AsinhStretch,
    PercentileInterval,
    ImageNormalize
)

from astropy.wcs import WCS

import warnings
from astropy.wcs import FITSFixedWarning

warnings.simplefilter("ignore", FITSFixedWarning)

# -------------------------------------------------
# PATHS
# -------------------------------------------------

cutout_dir = "/home/kapil-2208/lyman_alpha_morph/hubble_xdf/goods_cutout/cutout_comined_vitte"

catalog = pd.read_csv(
    "/home/kapil-2208/lyman_alpha_morph/hubble_xdf/vitte_combined_full_catalog.csv"
)

host_catalog = pd.read_csv(
    "/home/kapil-2208/lyman_alpha_morph/hubble_xdf/LAE_host_properties_catalog.csv"
)

# -------------------------------------------------
# FILTERS
# -------------------------------------------------

filters = [
    "F435W",
    "F606W",
    "F775W",
    "F814W",
    "F850LP",
    "F125W",
    "F160W",
    "F277W",
    "F356W",
    "F444W"
]

# -------------------------------------------------
# COLOR PALETTES
# -------------------------------------------------

palette_dict = {
    "magma": Magma256,
    "inferno": Inferno256,
    "viridis": Viridis256,
    "cubehelix": Cividis256,
    "bone": Greys256
}

# -------------------------------------------------
# READ CUTOUT FILES
# -------------------------------------------------

files = glob.glob(os.path.join(cutout_dir, "*.fits"))

id_dict = {}

for f in files:

    name = os.path.basename(f)
    parts = name.split("_")

    ID = int(parts[0])
    filt = parts[1]

    if ID not in id_dict:
        id_dict[ID] = {}

    id_dict[ID][filt] = f

ids = sorted(id_dict.keys())

current_index = 0

# -------------------------------------------------
# FIGURES
# -------------------------------------------------

sources = []

for i in range(10):
    sources.append(
        ColumnDataSource(
            data=dict(image=[np.zeros((10, 10))])
        )
    )

figs = []

for i in range(10):

    p = figure(
        width=250,
        height=250,
        tools="pan,wheel_zoom,reset"
    )

    p.xaxis.visible = False
    p.yaxis.visible = False

    p.image(
        image='image',
        x=0,
        y=0,
        dw=1,
        dh=1,
        source=sources[i],
        palette=palette_dict["magma"]
    )

    figs.append(p)

grid = gridplot(figs, ncols=5)

# -------------------------------------------------
# WIDGETS
# -------------------------------------------------

classification = RadioButtonGroup(
    labels=[
        "Single nucleus",
        "Double nucleus",
        "Irregular",
        "Unclear",
        "No source detected"
    ]
)

comment_box = TextAreaInput(title="Comment")

cmap_select = Select(
    title="Colormap",
    value="magma",
    options=list(palette_dict.keys())
)

brightness_slider = Slider(
    start=90,
    end=100,
    value=99,
    step=0.5,
    title="Percentile scale"
)

search_box = TextInput(title="Search ID")

# -------------------------------------------------
# INFO PANEL
# -------------------------------------------------

info_panel = Div(
    text="",
    width=500,
    height=80
)

# -------------------------------------------------
# HOST CATALOG PANEL
# -------------------------------------------------

catalog_panel = Div(
    text="",
    width=350,
    height=220,
    styles={
        "border": "2px solid gray",
        "padding": "12px",
        "border-radius": "10px",
        "background-color": "#f5f5f5",
        "font-size": "14px",
        "overflow-y": "auto"
    }
)

# -------------------------------------------------
# HIDDEN CURRENT ID
# -------------------------------------------------

current_id_div = Div(text="0", visible=False)

# -------------------------------------------------
# BUTTONS
# -------------------------------------------------

next_button = Button(label="Next")
prev_button = Button(label="Previous")
save_button = Button(label="Save")

amused_button = Button(
    label="Open in AMUSED",
    button_type="success"
)

# -------------------------------------------------
# AMUSED BUTTON CALLBACK
# -------------------------------------------------

amused_button.js_on_click(
    CustomJS(
        args=dict(current_id=current_id_div),
        code="""
        const id = current_id.text;
        const url =
            "https://amused.univ-lyon1.fr/project/UDF/browse/" + id;

        window.open(url, "_blank");
        """
    )
)

# -------------------------------------------------
# LOAD GALAXY
# -------------------------------------------------

def load_galaxy(index):

    ID = ids[index]

    current_id_div.text = str(ID)

    # -----------------------------------
    # MAIN CATALOG
    # -----------------------------------

    row = catalog[catalog["ID"] == ID].iloc[0]

    RA = row["RAJ2000"]
    DEC = row["DEJ2000"]
    z = row["zspec"]

    # -----------------------------------
    # HOST CATALOG
    # -----------------------------------

    host_row = host_catalog[
        host_catalog["VITTE_ID"] == ID
    ]

    if len(host_row) > 0:

        host_row = host_row.iloc[0]

        zspec_vitte = host_row["zspec_vitte"]
        zphot_uvudf = host_row["zphot_uvudf"]

        logM_uvudf = host_row["logM_uvudf"]
        logSFR_uvudf = host_row["logSFR_uvudf"]

        zphot_jades = host_row["zphot_jades"]

        zspec_astrodeep = host_row["zspec_astrodeep"]
        zphot_astrodeep = host_row["zphot_astrodeep"]

    else:

        zspec_vitte = np.nan
        zphot_uvudf = np.nan

        logM_uvudf = np.nan
        logSFR_uvudf = np.nan

        zphot_jades = np.nan

        zspec_astrodeep = np.nan
        zphot_astrodeep = np.nan

    # -----------------------------------
    # UPDATE INFO PANEL
    # -----------------------------------

    info_panel.text = f"""
    <b>ID:</b> {ID}
    &nbsp;&nbsp;

    <b>RA:</b> {RA:.5f}
    &nbsp;&nbsp;

    <b>DEC:</b> {DEC:.5f}
    &nbsp;&nbsp;

    <b>z:</b> {z:.3f}
    """

    # -----------------------------------
    # UPDATE HOST PANEL
    # -----------------------------------

    catalog_panel.text = f"""
    <div style="line-height:1.8;">

    <h3>Galaxy Properties</h3>

    <b>VITTE ID:</b> {ID}

    <br>

    <b>zspec_vitte:</b> {zspec_vitte:.3f}

    <br>

    <b>zphot_uvudf:</b> {zphot_uvudf:.3f}

    <br>

    <b>zphot_jades:</b> {zphot_jades:.3f}

    <br>

    <b>zspec_astrodeep:</b> {zspec_astrodeep:.3f}

    <br>

    <b>zphot_astrodeep:</b> {zphot_astrodeep:.3f}

    <br><br>

    <b>logM_uvudf:</b> {logM_uvudf:.2f}

    <br>

    <b>logSFR_uvudf:</b> {logSFR_uvudf:.2f}

    </div>
    """

    # -----------------------------------
    # LOAD IMAGES
    # -----------------------------------

    for i, filt in enumerate(filters):

        if filt in id_dict[ID]:

            hdu = fits.open(id_dict[ID][filt])

            data = hdu[0].data
            wcs = WCS(hdu[0].header)

            norm = ImageNormalize(
                data,
                interval=PercentileInterval(
                    brightness_slider.value
                ),
                stretch=AsinhStretch()
            )

            data = norm(data)

            sources[i].data = dict(image=[data])

            figs[i].renderers[0].glyph.dw = data.shape[1]
            figs[i].renderers[0].glyph.dh = data.shape[0]

            figs[i].renderers[0].glyph.color_mapper.palette = \
                palette_dict[cmap_select.value]

            figs[i].renderers = figs[i].renderers[:1]

            xc = data.shape[1] / 2
            yc = data.shape[0] / 2

            pixscale = abs(
                wcs.pixel_scale_matrix[0, 0]
            ) * 3600

            r = 0.5 / pixscale

            figs[i].scatter(
                x=[xc],
                y=[yc],
                marker="cross",
                size=20,
                color="yellow"
            )

            figs[i].circle(
                [xc],
                [yc],
                radius=r,
                line_color="red",
                fill_alpha=0
            )

            figs[i].title.text = filt

# -------------------------------------------------
# CALLBACKS
# -------------------------------------------------

def update_cmap(attr, old, new):
    load_galaxy(current_index)

cmap_select.on_change("value", update_cmap)

def update_brightness(attr, old, new):
    load_galaxy(current_index)

brightness_slider.on_change(
    "value",
    update_brightness
)

# -------------------------------------------------
# NAVIGATION
# -------------------------------------------------

def next_galaxy():

    global current_index

    current_index = (
        current_index + 1
    ) % len(ids)

    load_galaxy(current_index)

def prev_galaxy():

    global current_index

    current_index = (
        current_index - 1
    ) % len(ids)

    load_galaxy(current_index)

# -------------------------------------------------
# SEARCH
# -------------------------------------------------

def search_id(attr, old, new):

    global current_index

    if new.isdigit():

        ID = int(new)

        if ID in ids:

            current_index = ids.index(ID)

            load_galaxy(current_index)

search_box.on_change("value", search_id)

# -------------------------------------------------
# SAVE CLASSIFICATION
# -------------------------------------------------

def save_result():

    ID = ids[current_index]

    row = catalog[
        catalog["ID"] == ID
    ].iloc[0]

    data = {
        "ID": ID,
        "RA": row["RAJ2000"],
        "DEC": row["DEJ2000"],
        "zspec": row["zspec"],

        "classification":
        classification.labels[
            classification.active
        ]
        if classification.active is not None
        else "",

        "comment": comment_box.value
    }

    df = pd.DataFrame([data])

    file = "classification_results_new_22222.csv"

    if os.path.exists(file):

        df.to_csv(
            file,
            mode="a",
            header=False,
            index=False
        )

    else:

        df.to_csv(
            file,
            index=False
        )

# -------------------------------------------------
# BUTTON CALLBACKS
# -------------------------------------------------

next_button.on_click(next_galaxy)

prev_button.on_click(prev_galaxy)

save_button.on_click(save_result)

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------

layout = column(

    row(
        info_panel,
        catalog_panel
    ),

    grid,

    row(
        cmap_select,
        brightness_slider
    ),

    classification,

    comment_box,

    row(
        search_box,
        prev_button,
        save_button,
        next_button,
        amused_button
    )
)

curdoc().add_root(layout)

load_galaxy(0)


# In[ ]:




