package com.coda.settlement;

import java.io.InputStream;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;

/** Parses the daily settlement manifest uploaded by the acquirer. */
public class SettlementParser {

    public Document parseManifest(InputStream uploaded) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        DocumentBuilder builder = factory.newDocumentBuilder();
        return builder.parse(uploaded);
    }

    public Document parseTrustedSchema(InputStream bundled) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        return factory.newDocumentBuilder().parse(bundled);
    }

    public int countBatches(Document doc) {
        NodeList batches = doc.getElementsByTagName("batch");
        return batches.getLength();
    }
}
