package edu.psu.citeseerx.repository;

import edu.psu.citeseerx.domain.Document;
import edu.psu.citeseerx.domain.RepositoryService;

import java.io.IOException;
import java.util.HashMap;

public class RepositoryUtilities {
    public static String[] getFileTypes(RepositoryService repositoryService, String doi, String rep) throws IOException{
        HashMap<String,String> fileTypesQuery = new HashMap<String,String>();
        fileTypesQuery.put(Document.DOI_KEY, doi);
        fileTypesQuery.put(RepositoryService.REPOSITORYID, rep);
        return repositoryService.fileTypes(fileTypesQuery);
    }

    public static String getDocumentText(RepositoryService repositoryService, String doi, boolean bodyFile) throws DocumentUnavailableException, IOException {
        HashMap<String,String> parameters = new HashMap<String,String>();
        parameters.put(Document.DOI_KEY, doi);
        if (bodyFile) {
            parameters.put(RepositoryService.FILETYPE, RepositoryService.BODYFILE);
        }
        else {
            parameters.put(RepositoryService.FILETYPE, RepositoryService.TEXTFILE);
        }
        return repositoryService.getDocumentContent(parameters);
    }
}