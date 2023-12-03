// JavaScript function to generate 6 random unique values in order and populate form
function luckyDip() {

    // create empty set
    let draw = new Set();

    while (draw.size < 6) {
        min = 1;
        max = 60;

        // generate cryptographically secure random number
        let csRandomNumber = crypto.getRandomValues(new Uint32Array(1))[0] / 0xFFFFFFFF;

        // convert the csRandomNumber to an integer between 1 and 60
        let value = Math.floor(csRandomNumber * (max - min + 1) + min);

        // sets cannot contain duplicates, so value is only added if it does not exist in the set
        draw.add(value);
    }

    // turn set into an array
    let a = Array.from(draw);

    // sort array into size order
    a.sort(function (a, b) {
        return a - b;
    });

    // add values to fields in create draw form
    for (let i = 0; i < 6; i++) {
        document.getElementById("no" + (i + 1)).value = a[i];
    }
}