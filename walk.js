const fs = require('fs');
const path = require('path');
function walk(dir) {
  try {
    const files = fs.readdirSync(dir);
    files.forEach(f => {
      const p = path.join(dir, f);
      try {
        const stat = fs.statSync(p);
        if (stat.isDirectory()) {
          if (f === 'node_modules') return;
          walk(p);
        } else {
          try {
            const content = fs.readFileSync(p, 'utf8');
            if (content.includes('.svg')) {
              if (p.includes('avathi') || p.includes('vajrapoha') || p.includes('upli') || p.includes('basaveshwara')) {
                console.log(p);
              }
            }
          } catch(e){}
        }
      } catch(e){}
    });
  } catch(e){}
}
walk('C:/Users/ADMIN/omnirush.ai/india-explorer');
