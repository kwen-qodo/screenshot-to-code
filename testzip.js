const usaZipPattern = /^(\d{5})/;
const input = "12345-678";
let resolvedZip = 0;

const match = input.match(usaZipPattern);

if (match) {
  [, resolvedZip] = match; // destructure the first capturing group
}

console.log(resolvedZip); // "12345"