import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.resolve(import.meta.dirname,'..');const dir=path.join(root,'.build/browser-test');await fs.mkdir(dir,{recursive:true});
const b=await chromium.launch({channel:'chrome',headless:true});
try{
 const p=await b.newPage({viewport:{width:1280,height:720},acceptDownloads:true});
 await p.route('**/*',r=>/^(file:|data:|about:)/.test(r.request().url())?r.continue():r.abort());
 await p.goto(pathToFileURL(path.join(root,'outputs/northbridge-im.html')).href);
 assert.equal(await p.locator('.slide').count(),10);
 await p.keyboard.press('ArrowRight');assert.equal(await p.locator('#count').innerText(),'2 / 10');
 await p.locator('#sources').click();assert((await p.locator('#sourcePanel').innerText()).includes('PnL!D6'));
 await p.setViewportSize({width:390,height:844});await p.waitForFunction(()=>document.querySelector('.deck-stage').getBoundingClientRect().width<391);let box=await p.locator('.deck-stage').boundingBox();assert(Math.abs(box.width/box.height-16/9)<.001);assert(box.width<=391&&box.height<=845);
 await p.screenshot({path:path.join(dir,'phone.png')});
 await p.setViewportSize({width:1280,height:720});await p.evaluate(()=>deck.show(0));await p.keyboard.press('e');
 await p.locator('#cover-title').fill('Project Northbridge TEST');
 const dl=p.waitForEvent('download');await p.locator('#save').click();const download=await dl;await download.saveAs(path.join(dir,'edited.html'));
 await p.goto(pathToFileURL(path.join(dir,'edited.html')).href);assert.equal(await p.locator('#cover-title').innerText(),'Project Northbridge TEST');
 // Keep only the edited cover for a focused conversion regression.
 await p.evaluate(()=>document.querySelectorAll('.slide').forEach((s,i)=>{if(i)s.remove()}));await fs.writeFile(path.join(dir,'edited.html'),await p.content());
}finally{await b.close();}
const converter=path.join(root,'../skills/mna-information-memo/scripts/html_to_pptx.mjs');
execFileSync(process.execPath,[converter,path.join(dir,'edited.html'),path.join(dir,'edited.pptx'),path.join(dir,'previews')],{stdio:'pipe',env:process.env});
const txt=execFileSync(process.env.IM_PYTHON,['-c','import zipfile,sys;z=zipfile.ZipFile(sys.argv[1]);print(z.read("ppt/slides/slide1.xml").decode())',path.join(dir,'edited.pptx')],{encoding:'utf8'});
assert(txt.includes('Project Northbridge TEST'));
await fs.writeFile(path.join(root,'tests/browser-test-results.json'),JSON.stringify({passed:['Arrow-key navigation advances the deck.','Source panel resolves slide-specific PnL cell references.','Phone viewport preserves 16:9 stage without reflow.','Inline text edit survives Save HTML and reload.','Edited HTML text reaches native PowerPoint XML.']},null,2));
console.log('Browser navigation, mobile aspect ratio, edit/save and HTML-to-PPT regression passed.');
