const fs = require('fs');
const d = JSON.parse(fs.readFileSync('C:/Users/ADMIN/omnirush.ai/india-explorer/data/states/karnataka.json'));
function check(obj, path) {
  if (!path) path = '';
  if (Array.isArray(obj)) {
    obj.forEach((item, i) => check(item, path + '[' + i + ']'));
  } else if (typeof obj === 'object' && obj !== null) {
    Object.keys(obj).forEach(k => {
      if (k.toLowerCase().includes('image')) {
        console.log(path + '.' + k + ':', obj[k]);
      }
      check(obj[k], path + '.' + k);
    });
  }
}
check(d);
