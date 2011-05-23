

/**
 * Stop words which will be filtered out prior to any
 * further processing of the text being transformed.
 */
var stopWords = new Array (
	"a", "able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards",
	"again", "against", "ain't", "all", "allow", "allows", "almost", "alone", "along", "already", "also", 
	"although", "always", "am", "among", "amongst", "an", "and", "another", "any", "anybody", "anyhow", 
	"anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate",
	"are", "aren't", "around", "as", "aside", "ask", "asking", "associated", "at", "available", "away",
	"awfully", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand",
	"behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", 
	"both", "brief", "but", "by", "c'mon", "c's", "came", "can", "can't", "cannot", "cant", "cause", 
	"causes", "certain", "certainly", "changes", "clearly", "co", "com", "come", "comes", "concerning", 
	"consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", 
	"could", "couldn't", "course", "currently", "definitely", "described", "despite", "did", "didn't", 
	"different", "do", "does", "doesn't", "doing", "don't", "done", "down", "downwards", "during", "each", 
	"edu", "eg", "eight", "either", "else", "elsewhere", "enough", "entirely", "especially", "et", "etc", 
	"even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example",
	"except", "far", "few", "fifth", "first", "five", "followed", "following", "follows", "for", "former", 
	"formerly", "forth", "four", "from", "further", "furthermore", "get", "gets", "getting", "given", "gives"
	, "go", "goes", "going", "gone", "got", "gotten", "greetings", "had", "hadn't", "happens", "hardly", 
	"has", "hasn't", "have", "haven't", "having", "he", "he's", "hello", "help", "hence", "her", "here", 
	"here's", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him", "himself", "his",
	"hither", "hopefully", "how", "howbeit", "however", "i'd", "i'll", "i'm", "i've", "ie", "if", "ignored",
	"immediate", "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates", "inner", "insofar",
	"instead", "into", "inward", "is", "isn't", "it", "it'd", "it'll", "it's", "its", "itself", "just",
	"keep", "keeps", "kept", "know", "knows", "known", "last", "lately", "later", "latter", "latterly", 
	"least", "less", "lest", "let", "let's", "like", "liked", "likely", "little", "look", "looking", "looks",
	"ltd", "mainly", "many", "may", "maybe", "me", "mean", "meanwhile", "merely", "might", "more", "moreover",
	"most", "mostly", "much", "must", "my", "myself", "name", "namely", "nd", "near", "nearly", "necessary",
	"need", "needs", "neither", "never", "nevertheless", "new", "next", "nine", "no", "nobody", "non", "none",
	"noone", "nor", "normally", "not", "nothing", "novel", "now", "nowhere", "obviously", "of", "off", "often",
	"oh", "ok", "okay", "old", "on", "once", "one", "ones", "only", "onto", "or", "other", "others",
	"otherwise", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", "particular",
	"particularly", "per", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably",
	"provides", "que", "quite", "qv", "rather", "rd", "re", "really", "reasonably", "regarding", "regardless",
	"regards", "relatively", "respectively", "right", "said", "same", "saw", "say", "saying", "says", "second",
	"secondly", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible",
	"sent", "serious", "seriously", "seven", "several", "shall", "she", "should", "shouldn't", "since", "six",
	"so", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat",
	"somewhere", "soon", "sorry", "specified", "specify", "specifying", "still", "sub", "such", "sup", "sure",
	"t's", "take", "taken", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that's",
	"thats", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "there's", "thereafter",
	"thereby", "therefore", "therein", "theres", "thereupon", "these", "they", "they'd", "they'll", "they're",
	"they've", "think", "third", "this", "thorough", "thoroughly", "those", "though", "three", "through",
	"throughout", "thru", "thus", "to", "together", "too", "took", "toward", "towards", "tried", "tries",
	"truly", "try", "trying", "twice", "two", "un", "under", "unfortunately", "unless", "unlikely", "until",
	"unto", "up", "upon", "us", "use", "used", "useful", "uses", "using", "usually", "value", "various", "very",
	"via", "viz", "vs", "want", "wants", "was", "wasn't", "way", "we", "we'd", "we'll", "we're", "we've",
	"welcome", "well", "went", "were", "weren't", "what", "what's", "whatever", "when", "whence", "whenever",
	"where", "where's", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
	"which", "while", "whither", "who", "who's", "whoever", "whole", "whom", "whose", "why", "will", "willing", 
	"wish", "with", "within", "without", "won't", "wonder", "would", "would", "wouldn't", "yes", "yet", "you",
	"you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "zero" );


/**
 * Object that processes a document and transforms into a  
 * word frequency vector, ready for storage. Allows specification
 * of a minimum word length to be retained, as well as a minimum
 * frequency of occurrence for a word (support) in the text.
 */
function Parser( text, min_word_length, min_support ) {

	text = text.toLowerCase();
	text = stripScripts( text ); 
	text = stripTags( text );
	text = stripURLs( text );
	text = stripPunctuation( text );
	text = stripWhitespace( text ); 
	text = stripNonAlphaApostrophe( text );

	var wordList = text.split( " " );

	var fv = new Array();

	for ( var i in wordList ) {
		var word = wordList[ i ];
		if ( word.length >= min_word_length ) 
			if ( stopWords.indexOf( word ) == -1 )
				fv[ word ] = ( word in fv ) ? fv[ word ] + 1 : 1; 
	}

	var json = "{";
	for ( var i in fv ) {
		if ( fv[i] >= min_support ) {
			json += "\"" + i + '\":' + fv[i] + ",";
		}
	}

	if ( json.length > 1 )
	{
		json = json.substr( 0, json.length - 1 )
	}
	json += "}";

	this.min_word_length = min_word_length;
	this.min_support = min_support;
	this.totalWords = wordList.length;
	this.fv = json;
}


/**
 * Remove anything inside a script tag from the document
 */
function stripScripts( text ) {
	return text.replace( /<script[^>]*?>[\s\S]*?<\/script>/gi, '' );
}


/**
 * Remove any HTML remaining in the document
 */
function stripTags( text ) {
	return text.replace( /<[\/!]*?[^<>]*?>/gi, '' );
}


/**
 * Eliminate any extraneous whitespace (including newlines)
 */
function stripWhitespace( text ) {
	return text
		.replace( /\s+/gi, ' ')
		.replace( /^\s*/gi, '')
		.replace( /\s*$/gi, '');
}


/**
 * Remove any punctuation from the document, including brackets.
 * Note, hyphens are removed leaving two orphaned words, but
 * apostrophes are left in the text.
 */
function stripPunctuation( text ) {
	return text
		.replace( /["'.\-,:;?!(){}]/g, ' ');
}


/**
 * Remove any urls that remain embedded in the text, as they
 * are not of interest for our application.
 */
function stripURLs ( text )
{
	return text
		.replace( /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/gi, '' );
}


/**
 * Remove any character that is non-alphabetical apart from
 * apostrophes (including 
 */
function stripNonAlphaApostrophe( text ) {
	return text
		.replace( /[^ ]*[^a-zA-Z\' ]+[^ ]*( |$)/gi, '' );
}



