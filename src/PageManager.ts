import allContents from "./contents.json";

import { SectionDefinition } from "./types";

type SectionBlob = {
  name: string,
  title?: string,
  subsections?: SectionBlob[],
}


function toTitleCase(str: string) {
  return str.replace(/_/g, ' ').split(' ')
    .map(w => w[0].toUpperCase() + w.substr(1).toLowerCase())
    .join(' ')
}

class PageManager {
  pageDirectory: {[key: string]: SectionDefinition}
  rootSections: string[];
  orderedPages: string[];

  constructor() {
    this.pageDirectory = {};
    this.rootSections = [];
    this.orderedPages = [];

    allContents.subsections.forEach(section => {
      this.rootSections.push(section.name);
      this.insertSection(section, null);
    });

    this.generatePageOrder();
  }

  insertSection(section: SectionBlob, parent: string | null) {
    const subsection_names = section.subsections ? section.subsections.map(subsection => {
      this.insertSection(subsection, section.name);
      return subsection.name;
    }) : [];

    this.pageDirectory[section.name] = {
      name: section.name,
      title: section.title || toTitleCase(section.name),
      subsections: subsection_names,
      parent,
    }
  }

  generatePageOrder() {
    this.rootSections.forEach(s => this.pushSection(s));
  }

  pushSection(name: string) {
    this.orderedPages.push(name);
    this.get(name).subsections.map(s => this.pushSection(s));
  }

  get(name: string) {
    return this.pageDirectory[name];
  }

  indexOf(name: string) {
    return this.orderedPages.indexOf(name);
  }

  byIndex(index: number): SectionDefinition | undefined {
    if (index < 0) {
      return undefined;
    } else if (index >= this.orderedPages.length) {
      return undefined;
    } else {
      return this.get(this.orderedPages[index]);
    }
  }
}

const _PageManager = new PageManager();

export default _PageManager;
