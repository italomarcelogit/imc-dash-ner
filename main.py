import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import spacy
import spacy.cli
from spacy.displacy.render import DEFAULT_LABEL_COLORS
DEFAULT_LABEL_COLORS['PER'] = '#aa9cfc'
DEFAULT_LABEL_COLORS['MISC'] = '#9cc9cc'

text = '''O ministro da Economia, Paulo Guedes, participou de cinco encontros em seu primeiro dia de agenda nas Reuniões Anuais do Fundo Monetário Internacional e dos Conselhos de Governadores do Grupo Banco Mundial (IMF World Bank Annual Meetings), nesta terça-feira (11/10), em Washington, Estados Unidos.'''

spacy.cli.download('en_core_web_sm')
# python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

spacy.cli.download('pt_core_news_md')
# python -m spacy download pt_core_news_md
nlp_pt = spacy.load('pt_core_news_md')


def entname(name):
    return html.Span(name, style={
        "font-size": "0.8em",
        "font-weight": "bold",
        "line-height": "3",
        "border-radius": "0.35em",
        "text-transform": "uppercase",
        "vertical-align": "middle",
        "margin-left": "0.5rem"
    })


def entbox(children, color):
    return html.Mark(children, style={
        "background": color,
        "padding": "0.45em 0.6em",
        "margin": "0 0.25em",
        "line-height": "1",
        "border-radius": "0.35em",
    })


def entity(children, name):
    if type(children) is str:
        children = [children]

    children.append(entname(name))
    color = DEFAULT_LABEL_COLORS[name]
    return entbox(children, color)


def _render(doc):
    children = []
    last_idx = 0
    for ent in doc.ents:
        children.append(doc.text[last_idx:ent.start_char])
        children.append(
            entity(doc.text[ent.start_char:ent.end_char], ent.label_))
        last_idx = ent.end_char
    children.append(doc.text[last_idx:])
    return children


# ---- layout ---- #
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
server = app.server
app.title = 'NER - Named Entity Recognition'
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('NER - Named Entity Recognition'),
            html.H3('Libs: Dash Plotly to Dataviz and Spacy to NLP')
        ])
    ], justify='around'),
    dbc.Row(children=[
        dbc.Col(children=[
            dbc.Card([
                dbc.CardBody([
                    html.H4("NER Setup", className="card-title"),
                    dbc.Form([
                        dbc.Label('Choose your language', width='auto'),
                        dbc.RadioItems(id='_lang', value='pt',
                                       options=[
                                                {'label': 'Portuguese', 'value': 'pt'},
                                                {'label': 'English', 'value': 'en'}
                                                
                                       ]
                                       ),
                      
                        dbc.Label('Type or paste your text', width='auto'),
                        dbc.Textarea(id='_text', value=f'{text}', rows=15)

                    ])
                ])
            ])
        ], width=4),
        dbc.Col(children=[
            dbc.Card([
                dbc.CardBody([
                    html.H4("Resultado", className="card-title"),
                    html.Div(children={}, className="mx",
                             id='_result'),
                    dbc.Table(id='_table01', children={}, bordered=True, striped=True, hover=True),

                ])
            ],)
        ], width=8)
    ], justify='center'),
    dbc.Row([
    html.H5('@italomarcelogit')
    ])

])

# ------ callbacks ------ #
@app.callback(
    Output('_result', 'children'),
    Input('_text', 'value'),
    Input('_lang', 'value')
)
def find_NER(text, lang):
    try:
        if lang == 'pt':
            doc = nlp_pt(text)
        else:
            doc = nlp(text)
        r = _render(doc)
    except:
        r = text
        pass
    return r


@app.callback(
    Output('_table01', 'children'),
    Input('_text', 'value'),
    Input('_lang', 'value')
)
def create_Table01(text, lang):
    table_header = [
        html.Thead(html.Tr([html.Th("Text"), html.Th("Label Name")]))
    ]
    table_body = [html.Tbody([html.Tr([html.Td("None"), html.Td("None")])])]
    try:
        if lang == 'pt':
            doc = nlp_pt(text)
        else:
            doc = nlp(text)
        rows = []
        for e in doc.ents:
            row = html.Tr([html.Td(e.text), html.Td(e.label_)])
            rows.append(row)
        table_body = [html.Tbody(rows)]
    except:
        pass
    return table_header + table_body

if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
