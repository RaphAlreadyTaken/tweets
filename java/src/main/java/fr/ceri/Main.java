package fr.ceri;

import fr.ceri.entities.ElasticQuery;
import fr.ceri.entities.HashtagProcessor;
import fr.ceri.entities.WriterToFS;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.search.SearchHit;

import java.io.IOException;
import java.util.List;

public class Main
{
    public static void main(String[] args) throws IOException
    {
        WriterToFS writerToFS = new WriterToFS();

       String field = "hashtags";

       ElasticQuery query = new ElasticQuery("localhost", 9200, "http");
       SearchRequest request = query.buildElasticQuery(new String[]{field}, null);
       List<SearchHit> hits = query.sendElasticQuery(request);

       HashtagProcessor hashProc = new HashtagProcessor();

       hashProc.convertToHashtagMap(hits, field);
       hashProc.displayHashtagMap();
       writerToFS.writeToFS(hashProc.getHashMap(), hashProc.getTargetDataFile());

//         WordProcessor wordProc = new WordProcessor();
//         wordProc.convertToWordMapAndFormat();
//         writerToFS.writeToFS(wordProc.getWordList(), wordProc.getTargetDataFile());
    }
}
