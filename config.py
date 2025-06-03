from aqt import mw

PREDEFINED_SEARCH_SITES = {
    "English": {
        "Cambridge Dictionary": "https://dictionary.cambridge.org/dictionary/english/{}",
        "Oxford Dictionary": "https://www.oxfordlearnersdictionaries.com/definition/english/{}_1?q={}",
        "Merriam-Webster": "https://www.merriam-webster.com/dictionary/{}",
        "Longman Dictionary": "https://www.ldoceonline.com/dictionary/{}",
        "Collins Dictionary": "https://www.collinsdictionary.com/dictionary/english/{}",
        "Macmillan Dictionary": "https://www.macmillandictionary.com/search/?q={}",
        "Urban Dictionary": "https://www.urbandictionary.com/define.php?term={}",
        "Vocabulary.com": "https://www.vocabulary.com/dictionary/{}",
        "The Free Dictionary": "https://www.thefreedictionary.com/{}",
        "Dictionary.com": "https://www.dictionary.com/browse/{}"
    },
    "Tiếng Việt": {
        "Cambridge Việt": "https://dictionary.cambridge.org/dictionary/english-vietnamese/{}",
        "Dunno": "https://dunno.ai/search/word/{}?hl=vi",
        "Laban": "https://dict.laban.vn/find?type=1&query={}",
        "VDict": "https://vdict.com/{},1,0,0.html",
    },
    "Example": {
        "Dunno Examples": "https://dunno.ai/search/example/{}?hl=vi",
        "TraCau": "https://tracau.vn/?s={}",
        "Ludwig": "https://ludwig.guru/s/{}",
        "Sentence Stack": "https://sentencestack.com/q/{}",
        "Fraze.it": "https://fraze.it/n_search.jsp?q={}&l=0"
    },
    "Thesaurus": {
        "Thesaurus.com": "https://www.thesaurus.com/browse/{}",
        "Power Thesaurus": "https://www.powerthesaurus.org/{}",
        "Merriam-Webster Thesaurus": "https://www.merriam-webster.com/thesaurus/{}"
    },
    "Image": {
        "Google Images": "https://www.google.com/search?q={}&tbm=isch",
        "Bing Images": "https://www.bing.com/images/search?q={}",
        "Giphy": "https://giphy.com/search/{}",
        "Tenor": "https://tenor.com/search/{}"
    }
}

def get_config():
    return mw.addonManager.getConfig(__name__) or default_config()

def save_config(config):
    mw.addonManager.writeConfig(__name__, config)

def default_config():
    return {
        "note_type": "",
        "main_field": "",
        "configurable_fields": {},  # Format: {note_type_name: [field_name1, field_name2]}
        "field_display_states": {}, # Format: {note_type_name: {field_name: {"expanded": True/False}}}
        "field_search_configs": {}  # Existing: site selections for configured fields
    }