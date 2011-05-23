/**
 * Object that stores the relevant information for transmission
 * to the user's pref store.
 */
function Distillation( fv, url, duration, docName, totalWords ) {

	this.user = window.localStorage.getItem( "jid" );
	this.key = window.localStorage.getItem( "key" );
	this.fv = fv;
	this.docId = escape( url );
	this.duration = duration;
	this.docType = DOCUMENT_TYPE;
	this.appName = APPLICATION_NAME;
	this.mtime = Math.round ( new Date().getTime() / 1000 );
	this.docName = docName;
	this.totalWords = totalWords;
}


/**
 * Dedicated toJson function, currently required because
 * the frequency vector, fv, already arrives in json. 
 * TODO - make this more elegant with some reflection?
 */
Distillation.prototype.stringify = function() {
	return "{" + 
		"\"user\":\"" + this.user + "\"," +
		"\"key\":\"" + this.key + "\"," +
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