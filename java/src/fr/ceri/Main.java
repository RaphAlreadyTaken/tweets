package fr.ceri;

import fr.ceri.entities.WordProcessor;
import fr.ceri.entities.WriterToFS;

import java.io.IOException;

public class Main
{
    public static void main(String[] args) throws IOException
    {
        WriterToFS writerToFS = new WriterToFS();

//        String field = "hashtags";
//
//        ElasticQuery query = new ElasticQuery("localhost", 9200, "http");
//        SearchRequest request = query.buildElasticQuery(new String[]{field}, null);
//        List<SearchHit> hits = query.sendElasticQuery(request);
//
//        HashtagProcessor hashProc = new HashtagProcessor();
//        hashProc.convertToHashtagMap(hits, field);
//        hashProc.displayHashtagMap();
//
//        writerToFS.writeMapToFS(hashProc.getHashList(), hashProc.getTargetDataFile());

        WordProcessor wordProc = new WordProcessor();
        wordProc.convertToWordMapAndFormat();

        writerToFS.writeMapToFS(wordProc.getWordList(), wordProc.getTargetDataFile());
    }
}
