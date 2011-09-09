<html>
<head>
	<title>
		Prefstore - Data Analysis 2
	</title>

	<script type="text/javascript" src="http://www.google.com/jsapi">
	</script>
	
	<script type="text/javascript" src="./static/jquery-1.6.min.js">
	</script> 

	<script type="text/javascript">
		google.load('visualization', '1', {packages: ['table']});
	</script>

	<script type="text/javascript">
	var termTable;
	var data;
	var selection;

	var options = {'showRowNumber': true};

	/**
	 *
	 */
	function drawVisualization() {
    	
		var dataAsJson = {
			cols:[
				{id:'A',label:'Term',type:'string'},
				{id:'B',label:'Appearances',type:'number'},
				{id:'C',label:'In Documents',type:'number'},
				{id:'D',label:'Web Prevalence', type:'number'},
				{id:'E',label:'Relevence', type:'number'},
				{id:'F',label:'Last Seen (GMT)', type:'timeofday'}],
			rows:[{{data}}]
		};

		data = new google.visualization.DataTable( dataAsJson );
		
		options[ "page" ] = "enable";
		options[ "pageSize" ] = 20;
		options[ "pagingSymbols" ] = { prev: 'prev', next: 'next' };
		options[ "pagingButtonsConfiguration" ] = "auto";      

		termTable = new google.visualization.Table(document.getElementById( "termTable" ));
		termTable.draw( data, options );  

		google.visualization.events.addListener( termTable, 'select', function() {
			selection = termTable.getSelection();
			list = "";
			for ( i = 0; i < selection.length; i++ ) {
				if ( list.length>0 ) list+="</br>"
				list +=  data.getValue( selection[ i ].row, 0 );
			}
			$("#selectedList").html( list ); 

		});
    }
    
    google.setOnLoadCallback( drawVisualization );

    //-- sets the number of pages according to the user selection.
    function setPagination( numPages ) {
		if ( numPages ) {
			options[ "page" ] = "enable";
			options[ "pageSize" ] = parseInt( numPages, 10 );
		} else {
			options[ "page" ] = null;  
			options[ "pageSize" ] = null;
		}
		termTable.draw( data, options );  
    }
	
	</script>
</head>

<body style="font-family: georgia; font-size:12px; ">
	<div style="float:left; width:900px;">
		<div style="font-size:12px; margin-bottom:10px;">
			<div style="margin-top:15px; float:right; font-size:11px; vertical-align:bottom">
				{{message}}
			</div>
			<div>
				<span >Number rows/page:</span>
				<select style="font-size: 12px;" onchange="setPagination( this.value )">
					<option value="10">10</option>
					<option value="20">20</option>
					<option value="50">50</option>
					<option selected="selected" value="100">100</option>
					<option value="">all</option>
				</select>
			</div>
			
		</div>

		<div id="termTable">next</div>
	</div>

	<div style="text-align:center; margin:34 0 0 20; float:left; border:1px solid #fafafa; width:220px;">
		<div style="padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Selected Terms:
		</div>
		<div id="selectedList" style="min-height:50px; border:1px solid #eaeaea; background-color: #fafafa; padding:5px;"> 
		</div>
		
		<div style="margin-top:15px; padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Search For:
		</div>
		<div style="text-align:right; border:1px solid #eaeaea; background-color: #fafafa; padding:10 10 0 0;"> 
			<form name="searchForm" action="/data" method="GET" enctype="multipart/form-data">
				<select name="match_type" style="width:175px;">
%if match_type == 'exact':
					<option selected="selected" value="exact">The exact term...</option>
%else:
					<option value="exact">The exact term...</option>
%end

%if match_type == 'contains':
					<option selected="selected" value="contains">A term containing...</option>
%else:
					<option value="contains">A term containing...</option>
%end

%if match_type == 'starts':
					<option selected="selected" value="starts">A term starting with...</option>
%else:
					<option value="starts">A term starting with...</option>
%end

%if match_type == 'ends':
					<option selected="selected" value="ends">A term ending with...</option>
%else:
					<option value="ends">A term ending with...</option>
%end
				</select>					
				<input type="text" name="search_term" value="{{search_term}}" style="width:175px;"/><br/>
				<input type="hidden" name="type" value="search"/>
				<span><a href="javascript:document.searchForm.submit();">Search</a></span>
			</form>
		</div>

		<div style="margin-top:15px; padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Filter Terms:
		</div>
		<div style="text-align:right; border:1px solid #eaeaea; background-color: #fafafa; padding:10 10 0 0;"> 
			<form name="filterForm" action="/data" method="GET" enctype="multipart/form-data">
				<select name="direction" style="width:175px;">

%if direction == 'ASC':
					<option value="DESC">top 500 terms</option>
					<option selected="selected" value="ASC">bottom 500 terms</option>
%else:
					<option selected="selected" value="DESC">top 500 terms</option>
					<option value="ASC">bottom 500 terms</option>
%end

					
				</select><br/>
				<select name="order_by" style="width:175px;">

%if order_by == 'term':
					<option selected="selected" value="term">by alphabetical order</option>
%else:
					<option value="term">by alphabetical order</option>
%end

%if order_by == 'total_appearances':
					<option selected="selected" value="total_appearances">by total appearances</option>
%else:
					<option value="total_appearances">by total appearances</option>
%end

%if order_by == 'doc_appearances':
					<option selected="selected" value="doc_appearances">by doc appearances</option>
%else:
					<option value="doc_appearances">by doc appearances</option>
%end

%if order_by == 'prevalence':
					<option selected="selected" value="prevalence">by prevalence on web</option>
%else:
					<option value="prevalence">by prevalence on web</option>
%end

%if order_by == 'relevance':
					<option selected="selected" value="relevance">by relevence to you</option>
%else:
					<option value="relevance">by relevence to you</option>
%end

%if order_by == 'last_seen':
					<option selected="selected" value="last_seen">by time last seen</option>
%else:
					<option value="last_seen">by time last seen</option>
%end

				</select><br/>
				<input type="hidden" name="type" value="filter"/>
				<span><a href="javascript:document.filterForm.submit();">Fetch</a></span>
			</form>
		</div>

		
	</div>
</body>

</html>