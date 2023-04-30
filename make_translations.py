import googletrans as gt
import importlib

language_files = {
    "en_US": {"lang": "en"},
    "it_IT": {"lang": "it"},
    "pt_BR": {"lang": "pt"},
    "ru_RU": {"lang": "ru"},
    "zh_CN": {"lang": "zh-CN"},  # simplified chinese
}

for locale in language_files:
    language_files[locale]["local_str"] = importlib.import_module(f'languages.{locale}').local_str

messages_to_translate = {
    "not found any opencl-driver": "Not found any package that provides opencl-driver.",
}

for message in messages_to_translate:
    for locale in language_files:
        lang = language_files[locale]["lang"]
        translated_message = gt.translate(messages_to_translate[message], lang)
        language_files[locale]["local_str"][message] = translated_message

for file in language_files:
    with open(f'languages/{file}.py', 'w') as f:
        f.write("local_str = {\n")
        for msgid in language_files[file]["local_str"]:
            f.write("    \"%s\": \"%s\",\n" % (msgid, language_files[file]["local_str"][msgid]))
        f.write("}\n")
