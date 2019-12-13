package fr.ceri.entities;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

public class WriterToFS
{
    private ObjectMapper mapper = new ObjectMapper();

    public void writeMapToFS(Map<String, String> entities, String targetDataFile) throws IOException
    {
        String output = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(entities);
        BufferedWriter writer = new BufferedWriter(new FileWriter(targetDataFile));
        writer.write(output);
        writer.close();
    }
}
