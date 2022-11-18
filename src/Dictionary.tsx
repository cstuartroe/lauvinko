import React, { Component } from "react";

import PageHeader from "./PageHeader";
import {ApiResponse} from "./types";

type stem_category = "fientive" | "punctual" | "stative" | "uninflected";
type pta_abbrev = "gn" | "np" | "pt" | "pf" | "impt" | "imnp" | "fqnp" | "fqpt" | "inc";
type aspect = "Imperfective" | "Perfective" | "Frequentative" | "Inceptive";
type language = "pk" | "lv";

const languages_in_order: language[] = ["pk", "lv"];


const languageNames: {[key in language]: string} = {
    pk: "Classical Kasanic",
    lv: "Lauvìnko",
};

const ORIGIN_LANGUAGES = {
    "kasanic": "pk",
    "sanskrit": "pk",  // TODO
};

type Origin = keyof typeof ORIGIN_LANGUAGES;

type Form = {
    romanization: string,
    falavay: string,
}

type LangEntry = {
    forms: {[key: string]: Form},
    definition: string,
    category: stem_category,
}

type DictEntry = {
    languages: {[key in language]?: LangEntry},
    citation_form: pta_abbrev,
    alphabetization: string,
    origin: Origin,
}

const aspects: {[key in stem_category]: aspect[]} = {
    fientive: ["Imperfective", "Perfective", "Frequentative", "Inceptive"],
    punctual: ["Perfective", "Frequentative"],
    stative:  ["Imperfective", "Inceptive"],
    uninflected: [],
}

const aspect_tenses: {[key in stem_category]: {[key2 in aspect]: pta_abbrev[]}} = {
    fientive: {
        Imperfective: ["imnp", "impt"],
        Perfective: ["pf"],
        Frequentative: ["fqnp", "fqpt"],
        Inceptive: ["inc"]
    },
    punctual: {
        Imperfective: [],
        Perfective: ["np", "pt"],
        Frequentative: ["fqnp", "fqpt"],
        Inceptive: [],
    },
    stative: {
        Imperfective: ["gn", "pt"],
        Perfective: [],
        Frequentative: [],
        Inceptive: ["inc"],
    },
    uninflected: {
        Imperfective: [],
        Perfective: [],
        Frequentative: [],
        Inceptive: [],
    }
}

type InflectionRowProps = {
    entry: LangEntry,
    aspect: aspect,
    lang: language,
}

function InflectionRow(props: InflectionRowProps) {
    const { entry, aspect, lang } = props;

    const aspect_tense = aspect_tenses[entry.category][aspect];
    const forms = entry.forms;

    return <tr>
        <td>{aspect}</td>
        {aspect_tense.map(pta => (
            <td colSpan={3 - aspect_tense.length} key={pta} style={{textAlign: "center"}}>
                <span className="falavay">{forms[pta + ((lang === "lv") ? ".na" : "")].falavay}</span>
                <br/>
                <span style={{fontStyle: "italic"}}>{(lang === "lv") ?
                    forms[pta + ".au"].romanization + ", " + forms[pta + ".na"].romanization :
                    forms[pta].romanization
                }</span>
            </td>
        ))}
    </tr>
}

type LanguageEntryProps = {
    lang: language,
    entry: DictEntry,
}

type LanguageEntryState = {
    shown: boolean,
}

class LanguageEntry extends Component<LanguageEntryProps, LanguageEntryState> {
    constructor(props: LanguageEntryProps) {
        super(props);

        this.state = {
            shown: true,
        }
    }

    render() {
        const { lang, entry } = this.props;

        if (entry.languages[lang] === undefined) {
            return null;
        }

        const langEntry = entry.languages[lang] as LangEntry;

        const langname = languageNames[lang];

        let falavay_title = (lang == "lv") ?
          langEntry.forms[entry.citation_form + ".au"].falavay
          + " , " + langEntry.forms[entry.citation_form + ".na"].falavay :
          null;

        let title = (lang == "lv") ?
            langEntry.forms[entry.citation_form + ".au"].romanization
            + ", " + langEntry.forms[entry.citation_form + ".na"].romanization :
            langEntry.forms[entry.citation_form].romanization;

        return (
            <div>
                <h2 style={{textAlign: "left"}}>{langname}</h2>

                {(lang === "lv") ?
                <h3><span className={"falavay"}>{falavay_title}</span></h3>
                : null}

                <h3><span style={{fontStyle: "italic"}}>{title}</span></h3>

                <p>{langEntry.definition}</p>

                {langEntry.category === "uninflected" ? null :
                    <table>
                        <thead>
                        <tr>
                            <th colSpan={3}>
                                {langname} Inflection -{' '}
                                <a onClick={() => this.setState({shown: !this.state.shown})}>
                                    {this.state.shown ? "Hide" : "Show"}
                                </a>
                            </th>
                        </tr>
                        </thead>
                        {this.state.shown ? (
                            <tbody>
                                <tr>
                                    <th/>
                                    <th>Nonpast</th>
                                    <th>Past</th>
                                </tr>
                                {aspects[langEntry.category].map(aspect => (
                                  <InflectionRow
                                    entry={langEntry}
                                    aspect={aspect}
                                    lang={lang}
                                    key={aspect}
                                  />
                                ))}
                            </tbody>
                        ) : null}
                    </table>
                }
            </div>
        );
    }
}

function capitalize(s: string) {
    return s[0].toUpperCase() + s.substring(1).toLowerCase();
}

type DictionaryEntryProps = {
    entry: DictEntry,
}

class DictionaryEntry extends Component<DictionaryEntryProps> {
    render() {
        const { entry } = this.props;

        if (entry.languages.lv === undefined) {
            return null; // ought not to happen?
        }

        const citation_form = entry.languages.lv.forms[entry.citation_form + ".na"];

        return (
            <div className="entry">
                <h1 className="falavay">{citation_form.falavay}</h1>

                {/* TODO: copy link */}

                {/* TODO: source language */}

                {languages_in_order.map(lang => (
                  <LanguageEntry lang={lang} entry={entry} key={lang}/>
                ))}

                <hr/>
            </div>
        );
    }
}


// TODO: wtf was this?
const blurbs: {[key in Origin]?: string} = {
    // kasanic: "This is a list of Proto-Kasanic stems which became ",
}

type LanguageSectionProps = {
    origin: Origin,
    entries: {[key: string]: DictEntry},
    entry_ids: string[],
    showTitle: boolean,
}

class LanguageSection extends Component<LanguageSectionProps> {
    render() {
        const language_entry_ids = this.props.entry_ids.filter(id => (
          this.props.entries[id].origin === this.props.origin
        ));

        if (language_entry_ids.length === 0) {
            return null;
        }

        return (
          <div>
            {this.props.showTitle && (
              <h1>{capitalize(this.props.origin)}</h1>
            )}

            <p>{blurbs[this.props.origin]}</p>

            {this.props.entry_ids.map(id => (
                <DictionaryEntry
                  entry={this.props.entries[id]}
                  key={id}
                />
            ))}
          </div>
        );
    }
}

type DictionaryApiResponse = ApiResponse<{
    entries: {[key: string]: DictEntry},
}>

type DictionaryProps = {
    page_name: string,  // TODO this prop can be done away with
    origin_languages: Origin[],
}

type DictionaryState = {
    status: "pending",
    q: string | null,
    entries: {[key: string]: DictEntry},
}

class Dictionary extends Component<DictionaryProps, DictionaryState> {
    constructor(props: DictionaryProps) {
        super(props);

        this.state = {
            status: "pending",
            entries: {},
            q: null,
        }
    }

    componentDidMount() {
        const sp = new URLSearchParams(window.location.search);
        this.setState({q: sp.get('q')});

        fetch('/api/dict')
            .then(response => response.json())
            .then((data: DictionaryApiResponse) => {
                if (data.success) {
                    this.setState({entries: data.response.entries});
                }
            });
    }

    getAlph(name: string) {
        return this.state.entries[name].alphabetization;
    }

    compareKeys(name1: string, name2: string) {
        if (this.getAlph(name1) > this.getAlph(name2)) {
            return 1;
        } else {
            return -1;
        }
    }

    citation() {
        if (this.props.page_name === "loanword_dictionary") {
            return (
              <p>
                  All information about source languages adapted from{' '}
                  <a href="https://en.wiktionary.org/">English Wiktionary</a> and{' '}
                  <a href="https://sanskritdictionary.com/">sanskritdictionary.com</a>.
              </p>
            );
        } else {
            return null;
        }
    }

    languageEntries(): string[] {
        const all_entry_ids = Object.keys(this.state.entries);
        const language_entry_ids = all_entry_ids.filter(id => (
          this.props.origin_languages.includes(this.state.entries[id].origin)
        ));

        return language_entry_ids.sort((n1, n2) => this.compareKeys(n1, n2));
    }

    matchingEntries(entry_ids: string[]) {
        const { q } = this.state;

        if (q === null) { return entry_ids; }

        return entry_ids.filter(id => {
            const entry = this.state.entries[id];

            if (q.startsWith('@')) {
                return id.startsWith(q.substring(1));
            }

            for (const lang of Object.keys(entry.languages)) {
                const langEntry = entry.languages[lang as language];

                if (langEntry === undefined) {
                    continue;
                }

                if (langEntry.definition.toLowerCase().includes(q)) {
                    return true;
                }

                // TODO: other matches
            }

            return false;
        });
    }

    render() {
        const language_entry_ids = this.languageEntries();
        const entry_ids_to_show = this.matchingEntries(language_entry_ids);

        return (
            <div>
                <PageHeader name={this.props.page_name} show_title={true}/>

                <p>This dictionary has {language_entry_ids.length} entries!</p>

                <input
                  type="text"
                  value={this.state.q || ""}
                  onChange={event => this.setState({q: event.target.value})}
                />

                <hr/>

                {this.props.origin_languages.map(origin => (
                  <LanguageSection
                    origin={origin}
                    entries={this.state.entries}
                    entry_ids={entry_ids_to_show}
                    showTitle={this.props.origin_languages.length !== 1}
                    key={origin}
                  />
                ))}

                {this.citation()}

                <PageHeader name={this.props.page_name} show_title={false}/>
            </div>
        );
    }
}

export default Dictionary;
