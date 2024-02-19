import argparse

parser = argparse.ArgumentParser()
parser.add_argument('manifest', type=str, help='manifest of a book (toml file)')
parser.add_argument('-n', '--no-gen-toc', action='store_true')
args = parser.parse_args()
manifest_path: str = args.manifest
no_gen_toc: bool = args.no_gen_toc

import os.path as op

import epublib

manifest, chapters = epublib.parse(manifest_path)

book = epublib.EpubBook()

# add metadata
book.set_uid(manifest.id)
book.set_title(manifest.title)
book.set_language(manifest.language)
for author in manifest.authors:
    book.add_author(author)

# add cover image
if manifest.cover is not None:
    cover_path = op.join(op.dirname(manifest_path), manifest.cover)
    with open(cover_path, 'rb') as fp:
        book.set_cover('image/cover.png', fp.read())

# add main content
chps = [
    epublib.EpubHtml(
        title=chapter.title,
        file_name=f'chp{i}.xhtml',
        content=chapter.to_text().encode(),
    )
    for i, chapter in enumerate(chapters)
]
for chp in chps:
    book.add_item(chp)

# create table of contents
# - add manual link
# - add section
# - add auto created links to chapters


def gen_toc():
    toc = []
    it = ['', []]
    for i, chapter in enumerate(chapters):
        if chapter.level == 1:
            it = [chps[i], []]
            toc.append(it)
        elif chapter.level == 2:
            it[1].append(chps[i])
        else:
            print('error level:', chapter)
    return toc


book.toc = chps if no_gen_toc else gen_toc()

# add navigation files
book.add_item(epublib.EpubNcx())
book.add_item(epublib.EpubNav())

# define css style
style = '''
@namespace epub "http://www.idpf.org/2007/ops";

body {
font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}

h2 {
    text-align: left;
    text-transform: uppercase;
    font-weight: 200;
}

ol {
    list-style-type: none;
}

ol > li:first-child {
    margin-top: 0.3em;
}


nav[epub|type~='toc'] > ol > li > ol  {
list-style-type:square;
}


nav[epub|type~='toc'] > ol > li > ol > li {
    margin-top: 0.3em;
}

'''

# add css file
book.add_item(
    epublib.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style.encode(),
    )
)

# create spin, add cover page as first page
book.spine = ['cover', 'nav', *chps]

# create epub file
with epublib.EpubWriter(book) as writer:
    writer.write()
print(f'save at {writer.path}')
