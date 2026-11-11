const fs = require('fs');
const path = require('path');
const targets = ['avathi-hills.svg', 'vajrapoha-falls.svg', 'upli-buruj.svg', 'basaveshwara-temple-basavana-bagewadi.svg'];
function walk(dir) {
  try {
    const files = fs.readdirSync(dir);
    files.forEach(f => {
      const p = path.join(dir, f);
      try {
        const stat = fs.statSync(p);
        if (stat.isDirectory()) { if (f === 'node_modules') return; walk(p); return; }
        try {
          const content = fs.readFileSync(p, 'utf8');
          targets.forEach(t => {
            if (content.indexOf(t) !== -1) console.log(p + ': ' + t);
          });
        } catch(e){}
      } catch(e){}
    });
  } catch(e){}
}
walk('C:/Users/ADMIN/omnirush.ai/india-explorer');
