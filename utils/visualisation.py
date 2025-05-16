import plotly.graph_objects as go
from PIL import Image
import os
import base64


def create_kicks_visualization(kicks_df, x_min, x_max, y_min, y_max):
    """
    Create a visualization of kicks on a rugby league field.

    Args:
        kicks_df: DataFrame containing filtered kick data
        x_min, x_max, y_min, y_max: Field boundaries

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Add field SVG as background if available
    field_svg_path = "assets/field.svg"
    if os.path.exists(field_svg_path):
        # Read SVG file
        with open(field_svg_path, "rb") as svg_file:
            svg_data = svg_file.read()

        # Convert SVG to base64
        svg_base64 = base64.b64encode(svg_data).decode("utf-8")
        svg_src = f"data:image/svg+xml;base64,{svg_base64}"

        # Add SVG image to plot
        fig.add_layout_image(
            dict(
                source=svg_src,
                xref="x",
                yref="y",
                x=x_min,
                y=y_min,
                sizex=x_max - x_min,
                sizey=y_max - y_min,
                sizing="stretch",
                opacity=0.5,  # Full opacity for SVG
                layer="below"
            )
        )
    else:
        # Fallback to the original rectangle if SVG not found
        fig.add_shape(
            type="rect",
            x0=x_min,
            y0=y_min,
            x1=x_max,
            y1=y_max,
            line=dict(color="darkgreen", width=2),
            fillcolor="rgba(0, 100, 0, 0.1)"
        )

        # Add halfway line
        halfway_y = (y_max + y_min) / 2
        fig.add_shape(
            type="line",
            x0=x_min,
            y0=halfway_y,
            x1=x_max,
            y1=halfway_y,
            line=dict(color="white", width=2)
        )

    # Add kick lines
    for _, kick in kicks_df.iterrows():
        # Determine color based on outcome
        if "Outcome" in kick and kick["Outcome"] == "Try":
            line_color = "rgba(0, 255, 0, 1)"  # green try
            marker_colors = ["grey", "black"]
        elif "Outcome" in kick and kick["Outcome"] in ["Forces Dropout","40/20","Opp Error","Regained"]:
            line_color = "rgba(60, 60, 255, 0.8)"  # blue success
            marker_colors = ["grey", "black"]
        elif "Outcome" in kick and kick["Outcome"] in ["Kick Error", "20m Restart", "Own Error","Out on Full"]:
            line_color = "rgba(255, 60, 60, 0.8)"  # red failure
            marker_colors = ["grey", "black"]
        else:
            line_color = "rgba(0, 0, 0, 0.5)"  # black neutral
            marker_colors = ["grey", "black"]

        # Create hover text
        hover_text = f"Player: {kick['PN']}"
        if "Type" in kick:
            hover_text += f"<br>Type: {kick['Type']}"
        if "Outcome" in kick:
            hover_text += f"<br>Outcome: {kick['Outcome']}"
        if "GM" in kick:
            hover_text += f"<br>Time: {kick['GM']}"
        hover_text += f"<br>{kick['TeamName']} → {kick['OppositionName']}"

        # Add trace for kick
        fig.add_trace(
            go.Scatter(
                x=[kick["NX"], kick["nEX"]],
                y=[kick["NY"], kick["nEY"]],
                mode="lines+markers",
                name=kick['PN'] if 'PN' in kick else "",
                line=dict(width=2, color=line_color),
                marker=dict(size=[10, 8], color=marker_colors),
                hoverinfo="text",
                hovertext=hover_text
            )
        )

    # Set axes properties
    fig.update_xaxes(range=[x_min, x_max], showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(range=[y_max, y_min], showgrid=False, zeroline=False, visible=False)

    # Set layout
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Transparent paper
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig