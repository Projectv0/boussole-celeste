// Passe les textes du site au correcteur français de macOS (repris de Boussole émotionnelle).
//
//     swift orthographe.swift textes.json > fautes.json
//
// L'entrée est un tableau d'objets {source, texte} ; la sortie, un tableau
// {source, mot, contexte, suggestions}. Le correcteur est celui du système,
// le même que dans Pages ou Mail : il connaît le français, ses accents et ses
// élisions, ce qu'aucune liste de mots bricolée ne sait faire.
//
// Il ne sait pas tout : les noms propres, l'argot et les mots composés récents
// ressortent en faux positifs. La sortie se relit, elle ne s'applique pas.
import Foundation
import AppKit

struct Bloc: Decodable { let source: String; let texte: String }

let chemin = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : ""
guard let data = FileManager.default.contents(atPath: chemin),
      let blocs = try? JSONDecoder().decode([Bloc].self, from: data) else {
    FileHandle.standardError.write("fichier illisible : \(chemin)\n".data(using: .utf8)!)
    exit(1)
}

let correcteur = NSSpellChecker.shared
correcteur.setLanguage("fr")
let tag = NSSpellChecker.uniqueSpellDocumentTag()

var sortie: [[String: Any]] = []
for bloc in blocs {
    let ns = bloc.texte as NSString
    var debut = 0
    while debut < ns.length {
        let r = correcteur.checkSpelling(of: bloc.texte, startingAt: debut,
                                         language: "fr", wrap: false,
                                         inSpellDocumentWithTag: tag, wordCount: nil)
        if r.location == NSNotFound || r.length == 0 { break }
        let mot = ns.substring(with: r)
        // un peu de texte autour, pour pouvoir juger sans rouvrir la source
        let d = max(0, r.location - 34)
        let f = min(ns.length, r.location + r.length + 34)
        let contexte = ns.substring(with: NSRange(location: d, length: f - d))
        let sugg = correcteur.guesses(forWordRange: r, in: bloc.texte,
                                      language: "fr", inSpellDocumentWithTag: tag) ?? []
        sortie.append(["source": bloc.source, "mot": mot,
                       "contexte": contexte.replacingOccurrences(of: "\n", with: " "),
                       "suggestions": Array(sugg.prefix(4))])
        debut = r.location + r.length
    }
}
let d = try! JSONSerialization.data(withJSONObject: sortie, options: [.prettyPrinted])
FileHandle.standardOutput.write(d)
