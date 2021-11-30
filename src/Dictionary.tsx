// import React, { Component } from "react";
// const qs = require('query-string');
//
// import { parse_md_line } from "./Page";
// import PageHeader from "./PageHeader";
//
// const aspects = {
//     fientive: ["Imperfective", "Perfective", "Frequentative", "Inceptive"],
//     punctual: ["Perfective", "Frequentative"],
//     stative:  ["Imperfective", "Inceptive"]
// }
//
// const aspect_tenses = {
//     fientive: {
//         Imperfective: ["imnp", "impt"],
//         Perfective: ["pf"],
//         Frequentative: ["fqnp", "fqpt"],
//         Inceptive: ["inc"]
//     },
//     punctual: {
//         Perfective: ["np", "pt"],
//         Frequentative: ["fqnp", "fqpt"]
//     },
//     stative: {
//         Imperfective: ["gn", "pt"],
//         Inceptive: ["inc"]
//     }
// }
//
// function InflectionRow(props) {
//     let aspect = props.aspect;
//     let aspect_tense = aspect_tenses[props.entry.category][aspect];
//     let forms = props.entry.languages[props.lang].forms;
//     let lang = props.lang;
//
//     return <tr>
//         <td>{aspect}</td>
//         {aspect_tense.map(tense =>
//             <td colSpan={3 - aspect_tense.length} key={tense} style={{textAlign: "center"}}>
//                 <span className="lauvinko">{forms["$" + tense + "$" + ((lang === "lv") ? ".$na$" : "")].falavay}</span>
//                 <br/>
//                 <span style={{fontStyle: "italic"}}>{(lang === "lv") ?
//                     forms["$" + tense + "$.$au$"].transcription + ", " + forms["$" + tense + "$.$na$"].transcription :
//                     forms["$" + tense + "$"].transcription
//                 }</span>
//             </td>
//         )}
//     </tr>
// }
//
// class LanguageEntry extends Component {
//     state = {
//         shown: false
//     }
//
//     render() {
//         const lang = this.props.lang;
//         const langname = this.props.langname;
//         const entry = this.props.entry;
//         let falavay_title = (lang == "lv") ?
//             entry.languages[lang].forms[entry.citation_form + ".$au$"].falavay
//             + " , " + entry.languages[lang].forms[entry.citation_form + ".$na$"].falavay :
//             null;
//
//         let title = (lang == "lv") ?
//             entry.languages[lang].forms[entry.citation_form + ".$au$"].transcription
//             + ", " + entry.languages[lang].forms[entry.citation_form + ".$na$"].transcription :
//             entry.languages[lang].forms[entry.citation_form].transcription;
//
//         return (
//             <div>
//                 <h2 style={{textAlign: "left"}}>{langname}</h2>
//
//                 {(lang === "lv") ?
//                 <h3><span className={"lauvinko"}>{falavay_title}</span></h3>
//                 : null}
//
//                 <h3><span style={{fontStyle: "italic"}}>{title}</span></h3>
//
//                 <p>{parse_md_line(entry.languages[lang].definition)}</p>
//                 {entry.category === "uninflected" ? null :
//                     <table>
//                         <thead>
//                         <tr>
//                             <th colSpan="3">
//                                 {langname} Inflection - <a
//                                 onClick={() => this.setState({shown: !this.state.shown})}>
//                                     {this.state.shown ? "Hide" : "Show"}
//                                 </a>
//                             </th>
//                         </tr>
//                         </thead>
//                         {this.state.shown ?
//                             <tbody>
//                             <tr>
//                                 <th></th>
//                                 <th>Nonpast</th>
//                                 <th>Past</th>
//                             </tr>
//                             {aspects[entry.category].map(aspect => <InflectionRow entry={entry} aspect={aspect}
//                                                                                   lang={lang}
//                                                                                   key={aspect}/>)}
//                             </tbody>
//                             : null}
//                     </table>
//                 }
//             </div>
//         );
//     }
// }
//
// const languages = [["pk", "Classical Kasanic"], ["lv", "Lauvìnko"], ["bt", "Botharu"]];
//
// const ORIGIN_LANGUAGES = {
//     "kasanic": "pk",
//     "sanskrit": "sa",
//     "malay": "ms",
//     "arabic": "ar",
//     "tamil": "ta",
//     "hokkien": "hk",
//     "portuguese": "pt",
//     "dutch": "nl",
//     "english": "en"
// };
//
// function capitalize(s) {
//     return s[0].toUpperCase() + s.substring(1).toLowerCase();
// }
//
// class DictionaryEntry extends Component {
//     state = {
//         copied_opacity: 0
//     }
//
//     fadeLink() {
//         if (this.state.copied_opacity > 0) {
//             this.setState({copied_opacity: this.state.copied_opacity - 1}, () => {
//                 setTimeout(this.fadeLink.bind(this), 30);
//             });
//         }
//     }
//
//     copylink() {
//         let copyText = document.getElementById(this.props.id + "-link");
//         copyText.select();
//         copyText.setSelectionRange(0, 99999);
//         document.execCommand("copy");
//
//         this.setState({copied_opacity: 50}, this.fadeLink.bind(this));
//     }
//
//     render() {
//         const entry = this.props.entry;
//         const citation_form = entry.languages.lv.forms[entry.citation_form + ".$na$"];
//         const origin_lang = ORIGIN_LANGUAGES[entry.origin];
//
//         return (
//             <div className="entry">
//                 <h1 className="lauvinko">{citation_form.falavay}</h1>
//                 <p style={{position: "absolute", top: 0, right: 0, textAlign: "right"}}>
//                     <a onClick={this.copylink.bind(this)}>
//                         copy link
//                     </a><br/>
//                     <span id={this.props.id + "-copied"} style={{opacity: this.state.copied_opacity + "%"}}>
//                         link copied!
//                     </span><br/>
//                     <input type="text"
//                            value={document.location.protocol + "//" +
//                            document.location.host + "/lauvinko/" + this.props.page_id + "?q=@" + this.props.id}
//                            id={this.props.id + "-link"} style={{opacity: 0}} onChange={() => null}/>
//                 </p>
//
//                 {(entry.origin !== "kasanic") ?
//                     <p>
//                         From {capitalize(entry.origin)} {entry.languages[origin_lang].forms["$gn$"].native} {}
//                         <span style={{fontStyle: "italic"}}>{entry.languages[origin_lang].forms["$gn$"].transcription}</span>
//                         {' "' + entry.languages[origin_lang].definition + '"'}
//                     </p>
//                 : null}
//
//                 {languages.map(pair => entry.languages[pair[0]] ?
//                     <LanguageEntry lang={pair[0]} langname={pair[1]} entry={entry} key={pair[0]}/> : null
//                 )}
//                 <hr/>
//             </div>
//         );
//     }
// }
//
// const blurbs = {
//     "kasanic": "This is a list of Proto-Kasanic stems which became ",
//     "sanskrit": "",
//     "malay": "",
//     "arabic": ""
// }
//
// class LanguageSection extends Component {
//     render() {
//         return (this.props.entry_ids.length > 0) ? <div>
//             {this.props.title ? <h1>{capitalize(this.props.origin)}</h1> : null}
//             <p>{blurbs[this.props.origin]}</p>
//             {this.props.entry_ids.map(id =>
//                 <DictionaryEntry id={id} entry={this.props.entries[id]} key={id} page_id={this.props.page_id}/>
//                 )}
//         </div> : null;
//     }
// }
//
// function removeAccents(s) {
//     return s.replace(/á/g, 'a').replace(/à/g, 'a').replace(/é/g, 'e').replace(/è/g, 'e')
//         .replace(/í/g, 'i').replace(/ì/g, 'i').replace(/ó/g, 'o').replace(/ò/g, 'o');
// }
//
// function entryMatch(entry, ident, q) {
//     if (q.startsWith('@')) {
//         return ident.startsWith(q.substring(1));
//     }
//
//     for (const lang of Object.keys(entry.languages)) {
//         if (entry.languages[lang].definition.toLowerCase().includes(q)) {
//             return true;
//         }
//         for (const form of Object.keys(entry.languages[lang].forms)) {
//             let t = entry.languages[lang].forms[form].transcription.toLowerCase();
//             if (t.includes(q) || removeAccents(t).includes(q)) {
//                 return true;
//             }
//         }
//     }
//
//     return false;
// }
//
// class Dictionary extends Component {
//     state = {
//         status: "pending",
//         length: null,
//         entries: {},
//         q: ""
//     };
//
//     componentDidMount() {
//         let q = qs.parse(this.props.location.search).q;
//         if (q) {
//             this.setState({q: q});
//         }
//
//         fetch('/lauvinko/dict')
//             .then(response => {
//                 if (response.status !== 200) {
//                     return {};
//                 }
//                 return response.json();
//             })
//             .then(data => this.setState(data));
//     }
//
//     getAlph(id) {
//         let entry = this.state.entries[id];
//         return entry.languages.lv.forms[entry.citation_form + ".$na$"].transcription;
//     }
//
//     compareKeys(a, b) {
//         if (this.getAlph(a) > this.getAlph(b)) {
//             return 1;
//         } else {
//             return -1;
//         }
//     }
//
//     render() {
//         let entry_ids = Object.keys(this.state.entries);
//         entry_ids = entry_ids.filter(id => this.props.origins.includes(this.state.entries[id].origin));
//         let dict_size = entry_ids.length;
//         entry_ids = entry_ids.filter(id => entryMatch(this.state.entries[id], id, this.state.q.toLowerCase()));
//         entry_ids = entry_ids.sort(this.compareKeys.bind(this));
//
//         return (
//             <div>
//                 <PageHeader contents={this.props.contents} id={this.props.page_id}/>
//                 {this.props.page_id === "loanword_dictionary" ?
//                     <p>All information about source languages adapted from {}
//                         <a href="https://en.wiktionary.org/">English Wiktionary</a> and {}
//                         <a href="https://sanskritdictionary.com/">sanskritdictionary.com</a>.</p>
//                     : null}
//                 <p>This dictionary has {dict_size} entries!</p>
//                 <input type="text" value={this.state.q}
//                        onChange={event => this.setState({q: event.target.value})}/>
//                 <hr/>
//                 {this.props.origins.map(origin => <LanguageSection origin={origin} entries={this.state.entries}
//                                                                    entry_ids={entry_ids.filter(id => (this.state.entries[id].origin === origin))}
//                                                                    title={this.props.origins.length !== 1}
//                                                                    page_id={this.props.page_id} key={origin}/>)}
//             </div>
//         );
//     }
// }
//
// export default Dictionary;

export default null;