/**
 * Object that stores the relevant information for transmission
 * to the user's pref store.
 */
function Distillation( fv, url, duration, docName, totalWords ) {

	this.fv = fv;
	this.docId = escape( url );
	this.duration = duration;
	this.docType = escape( DOCUMENT_TYPE );
	this.appName = escape( APPLICATION_NAME );
	this.mtime = Math.round ( new Date().getTime() / 1000 );
	this.docName = escape( docName );
	this.totalWords = totalWords;
}


/**
 * Dedicated toJson function, currently required because
 * the frequency vector, fv, already arrives in json. 
 * TODO - make this more elegant with some reflection?
 */
Distillation.prototype.stringify = function() {
	return "{" + 
		"\"docId\":\"" + this.docId + "\"," +
		"\"docName\":\"" + this.docName + "\"," +
		"\"docType\":\"" + this.docType + "\"," +
		"\"totalWords\":" + this.totalWords + "," +
		"\"appName\":\"" + this.appName + "\"," +
		"\"duration\":" + this.duration + "," +
		"\"mtime\":" + this.mtime + "," +
		"\"fv\":" + this.fv + 
		"}";
}