const { process, minimizeJs, rename } = require('delphi-cmu-buildtools');

Promise.all([
    process('*.+(coffee|js|py|R)', [], { srcDir: './src/client', dstDir: './build/lib' }),
    process('*.js', [minimizeJs(), rename((f) => f.replace('.js', '.min.js'))], { srcDir: './src/client', dstDir: './build/lib' }),
]).then((r) => console.log(r.flat()));