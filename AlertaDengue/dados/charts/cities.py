from copy import deepcopy

import pandas as pd
import plotly.graph_objs as go
from django.utils.translation import gettext as _
from plotly.subplots import make_subplots


class ReportCityCharts:
    @classmethod
    def create_incidence_chart(
        cls,
        df: pd.DataFrame,
        year_week: int,
        threshold_pre_epidemic: float,
        threshold_pos_epidemic: float,
        threshold_epidemic: float,
    ):
        """
        @see: https://stackoverflow.com/questions/45526734/
            hide-legend-entries-in-a-plotly-figure
        :param df:
        :param year_week:
        :param threshold_pre_epidemic: float,
        :param threshold_pos_epidemic: float
        :param threshold_epidemic: float
        :return:
        """
        df = df.reset_index()[
            ["SE", "incidência", "casos notif.", "level_code"]
        ]

        df["SE"] = df.SE.map(lambda v: "%s/%s" % (str(v)[:4], str(v)[-2:]))

        k = "incidência"

        df[_("alerta verde")] = df[df.level_code == 1][k]
        df[_("alerta amarelo")] = df[df.level_code == 2][k]
        df[_("alerta laranja")] = df[df.level_code == 3][k]
        df[_("alerta vermelho")] = df[df.level_code == 4][k]

        df[_("limiar epidêmico")] = threshold_epidemic
        df[_("limiar pós epidêmico")] = threshold_pos_epidemic
        df[_("limiar pré epidêmico")] = threshold_pre_epidemic

        figure = make_subplots(specs=[[{"secondary_y": True}]])

        figure.add_trace(
            go.Scatter(
                x=df["SE"],
                y=df["casos notif."],
                name=_("Notificações"),
                marker={"color": "rgb(33,33,33)"},
                text=df.SE.map(lambda v: "{}".format(str(v)[-2:])),
                hoverinfo="text",
                hovertemplate=_("Semana %{text}<br>%{y:1f} Casos")
                + "<extra></extra>",
            ),
            secondary_y=True,
        )

        ks_limiar = [
            _("limiar pré epidêmico"),
            _("limiar pós epidêmico"),
            _("limiar epidêmico"),
        ]

        colors = ["rgb(0,255,0)", "rgb(255,150,0)", "rgb(255,0,0)"]

        for k, c in zip(ks_limiar, colors):
            figure.add_trace(
                go.Scatter(
                    x=df["SE"],
                    y=df[k],
                    y0=df["incidência"],
                    name=k.title(),
                    marker={"color": c},
                    text=df.SE.map(lambda v: "{}".format(str(v)[-2:])),
                    hoverinfo="text",
                    hovertext=df["incidência"],
                    hovertemplate=_("Semana %{text}<br>%{y:1f} Incidências")
                    + "<extra></extra>",
                ),
                secondary_y=False,
            )

        ks_alert = [
            _("alerta verde"),
            _("alerta amarelo"),
            _("alerta laranja"),
            _("alerta vermelho"),
        ]

        colors = [
            "rgb(0,255,0)",
            "rgb(255,255,0)",
            "rgb(255,150,0)",
            "rgb(255,0,0)",
        ]

        for k, c in zip(ks_alert, colors):
            figure.add_trace(
                go.Bar(
                    x=df["SE"],
                    y=df[k],
                    marker={"color": c},
                    name=k.title(),
                    text=df.SE.map(lambda v: "{}".format(str(v)[-2:])),
                    hoverinfo="text",
                    hovertemplate=_("Semana %{text}<br>%{y:1f} Incidências")
                    + "<extra></extra>",
                ),
                secondary_y=False,
            )

        figure.update_layout(
            title=(
                _("Limiares de incidência:")
                + "<br>"
                + "".ljust(8)
                + _("pré epidêmico=")
                + f"{threshold_pre_epidemic:.1f}".ljust(8)
                + _("pós epidêmico=")
                + f"{threshold_pos_epidemic:.1f}".ljust(8)
                + _("epidêmico=")
                + f"{threshold_epidemic:.1f}"
            ),
            font=dict(family="sans-serif", size=12, color="#000"),
            xaxis=dict(
                title=_("Período (Ano/Semana)"),
                tickangle=-60,
                nticks=len(df) // 4,
                showline=False,
                showgrid=True,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=0,
                gridcolor="rgb(176, 196, 222)",
                ticks="outside",
                tickfont=dict(
                    family="Arial", size=12, color="rgb(82, 82, 82)"
                ),
            ),
            yaxis=dict(
                title=_("Incidência"),
                showline=False,
                showgrid=True,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=0,
                gridcolor="rgb(176, 196, 222)",
            ),
            showlegend=True,
            legend=dict(
                traceorder="normal",
                font=dict(family="sans-serif", size=12, color="#000"),
                bgcolor="#FFFFFF",
                bordercolor="#E2E2E2",
                borderwidth=1,
            ),
            plot_bgcolor="rgb(255, 255, 255)",
            paper_bgcolor="rgb(245, 246, 249)",
            width=1100,
            height=500,
        )

        figure.update_yaxes(
            title_text=_("Casos Notificados"),
            secondary_y=True,
            showline=False,
            showgrid=True,
            showticklabels=True,
            linecolor="rgb(204, 204, 204)",
            linewidth=0,
            gridcolor="rgb(204, 204, 204)",
        )

        for trace in figure["data"]:
            if trace["name"] == "casos notif.":
                trace["visible"] = "legendonly"

        return figure.to_html()

    @classmethod
    def create_climate_chart(
        cls,
        df: pd.DataFrame,
        var_climate,
    ):
        """
        :param df:
        :param var_climate:
        :return:
        """

        varcli_keys = list(var_climate.keys())
        varcli_values = list(var_climate.values())

        df_climate = deepcopy(df[["SE", *varcli_keys]])

        df_climate["SE"] = df_climate.SE.map(
            lambda v: "%s/%s" % (str(v)[:4], str(v)[-2:])
        )

        df_climate[f"threshold_{varcli_keys[0]}"] = var_climate.get(
            varcli_keys[0]
        )[1]

        figure = make_subplots(specs=[[{"secondary_y": True}]])

        figure.add_trace(
            go.Scatter(
                x=df_climate["SE"],
                y=df_climate[varcli_keys[0]],
                name=f"{varcli_keys[0]}",
                # fill='tonextx',
                marker={"color": "rgb(255, 204, 153)"},
                text=df_climate.SE.map(lambda v: "{}".format(str(v)[-2:])),
                hoverinfo="text",
                hovertemplate=("{}: {} <br>" "{}{}" "<extra></extra>").format(
                    _("Semana"), "%{text}", "%{y:1f}", varcli_values[0][0]
                ),
            ),
            secondary_y=False,
        )

        figure.add_trace(
            go.Scatter(
                x=df_climate["SE"],
                y=df_climate[f"threshold_{varcli_keys[0]}"],
                name=("{} {}{}").format(
                    _("Limiar favorável"),
                    varcli_values[0][1],
                    varcli_values[0][0][0:2],
                ),
                marker={"color": "rgb(255,150,0)"},
                text=df_climate.SE.map(lambda v: "{}".format(str(v)[-2:])),
                hoverinfo="text",
                hovertemplate=(
                    "{}: {} <br>" "{}: {}{}" "<extra></extra>"
                ).format(
                    _("Semana"),
                    "%{text}",
                    _("Limiar favorável"),
                    "%{y:1f}",
                    varcli_values[0][0][0:2],
                ),
            ),
            secondary_y=False,
        )

        if len(varcli_keys) == 2:

            df_climate[f"threshold_{varcli_keys[1]}"] = var_climate.get(
                varcli_keys[1]
            )[1]
            figure.add_trace(
                go.Scatter(
                    x=df_climate["SE"],
                    y=df_climate[varcli_keys[1]],
                    name=f"{varcli_keys[1]}",
                    # fill='tonextx',
                    marker={"color": "rgb(173, 216, 230)"},
                    text=df_climate.SE.map(lambda v: f"{str(v)[-2:]}"),
                    hoverinfo="text",
                    hovertemplate=(
                        "{}: {} <br>" "{}{}" "<extra></extra>"
                    ).format(
                        _("Semana"), "%{text}", "%{y:1f}", varcli_values[1][0]
                    ),
                ),
                secondary_y=True,
            )

            figure.add_trace(
                go.Scatter(
                    x=df_climate["SE"],
                    y=df_climate[f"threshold_{varcli_keys[1]}"],
                    name=("{} {}{}").format(
                        _("Limiar favorável"),
                        varcli_values[1][1],
                        varcli_values[1][0][0:2],
                    ),
                    marker={"color": "rgb(51, 172, 255)"},
                    text=df_climate.SE.map(lambda v: "{}".format(str(v)[-2:])),
                    hoverinfo="text",
                    hovertemplate=(
                        "{}: {} <br>" "{}: {}{}" "<extra></extra>"
                    ).format(
                        _("Semana"),
                        "%{text}",
                        _("Limiar favorável"),
                        "%{y:1f}",
                        varcli_values[1][0][0:2],
                    ),
                ),
                secondary_y=True,
            )

            figure.update_yaxes(
                title_text=f"{varcli_values[1][0]}", secondary_y=True
            )

        figure.update_layout(
            hovermode="x",
            hoverlabel=dict(
                font_size=12,
                font_family="Rockwell",
            ),
            title=_("Condições climáticas para transmissão"),
            xaxis=dict(
                title=_("Período (Ano/Semana)"),
                tickangle=-60,
                nticks=len(df_climate) // 4,
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=0,
                gridcolor="rgb(176, 196, 222)",
            ),
            yaxis=dict(
                title=f"{varcli_values[0][0]}",
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=0,
                gridcolor="rgb(176, 196, 222)",
            ),
            showlegend=True,
            margin=dict(l=90, r=10, t=130, b=20),
            legend=dict(
                orientation="h",
                yanchor="middle",
                xanchor="right",
                y=1.10,
                x=0.94,
                font=dict(family="sans-serif", size=12, color="#000"),
                bgcolor="#FFFFFF",
                bordercolor="#E2E2E2",
                borderwidth=1,
            ),
            plot_bgcolor="rgb(255, 255, 255)",
            paper_bgcolor="rgb(245, 246, 249)",
            width=1100,
            height=550,
        )

        return figure.to_html()

    @classmethod
    def create_tweet_chart(cls, df: pd.DataFrame, year_week):
        """
        :param df:
        :param var_climate:
        :param year_week:
        :param climate_crit:
        :param climate_title:
        :return:
        """

        df_tweet = df.reset_index()[["SE", "tweet"]]
        # df_tweet = df_tweet[df_tweet.SE >= year_week - 200]

        df_tweet["SE"] = df_tweet.SE.map(
            lambda v: "%s/%s" % (str(v)[:4], str(v)[-2:])
        )

        df_tweet.rename(columns={"tweet": "menções"}, inplace=True)

        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=df_tweet["SE"],
                y=df_tweet["menções"],
                name=_("Menções em tweets"),
                marker={"color": "rgb(0,0,255)"},
                text=df_tweet.SE.map(lambda v: "{}".format(str(v)[-2:])),
                hoverinfo="text",
                hovertemplate=_("Semana %{text} : %{y} Tweets")
                + "<extra></extra>",
            )
        )

        figure.update_layout(
            title=_("Menções na mídia social"),
            xaxis=dict(
                title=_("Período (Ano/Semana)"),
                tickangle=-60,
                nticks=len(df_tweet) // 4,
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=0,
                gridcolor="rgb(176, 196, 222)",
            ),
            yaxis=go.layout.YAxis(
                title="Tweets",
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor="rgb(204, 204, 204)",
                linewidth=0,
                gridcolor="rgb(176, 196, 222)",
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                xanchor="auto",
                y=1.01,
                x=1,
                font=dict(family="sans-serif", size=12, color="#000"),
                bgcolor="#FFFFFF",
                bordercolor="#E2E2E2",
                borderwidth=1,
            ),
            plot_bgcolor="rgb(255, 255, 255)",
            paper_bgcolor="rgb(245, 246, 249)",
            width=1100,
            height=450,
        )

        return figure.to_html()
