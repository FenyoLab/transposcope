//http://www.kryptonite-dove.com/blog/load-json-file-locally-using-pure-javascript

function loadJSON(callback, filename) {
    'use strict';
    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', 'json/' + area + '/' + patientFolder + "/" + type + "/" + filename + '.json.gz.txt', true);
    if (filename !== "table_info") {
        xobj.addEventListener("progress", updateProgress);
        xobj.addEventListener("load", transferComplete);
    }
    xobj.onreadystatechange = function () {
        if (xobj.readyState === 4) {
            if (xobj.status === 200) {
//                console.log("fresh?");
                // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode


                // Get some base64 encoded binary data from the server. Imagine we got this:
                var b64Data     = xobj.responseText;
//                console.log(b64Data);
                // Decode base64 (convert ascii to binary)
                b64Data = b64Data.replace(/\s/g, '');
                var strData     = atob(b64Data);

                // Convert binary string to character-number array
                var charData    = strData.split('').map(function(x){return x.charCodeAt(0);});

                // Turn number array into byte-array
                var binData     = new Uint8Array(charData);

                // Pako magic
                var data        = pako.inflate(binData);

                // Convert gunzipped byteArray back to ascii string:
                var strData = _arrayBufferToBase64(data)
//                for (var x = 0;x < 10;x++)
//                    strData     = String.fromCharCode.apply(String, data);



                // Output to console
//                console.log(strData);

//                return asciistring;
                callback(strData);
//                callback(xobj.responseText);
            }
        }
    };
    xobj.send(null);
}

function _arrayBufferToBase64(uarr) {
    var strings = [], chunksize = 0xffff;
    var len = uarr.length;

    for (var i = 0; i * chunksize < len; i++){
        strings.push(String.fromCharCode.apply(null, uarr.subarray(i * chunksize, (i + 1) * chunksize)));
    }

    return strings.join("");
}

function updateProgress (oEvent) {
  if (oEvent.lengthComputable) {
    var percentComplete = oEvent.loaded / oEvent.total;
    loading(percentComplete);
  } else {
    console.log("sizeUnknown");
    // Unable to compute progress information since the total size is unknown
  }
}
