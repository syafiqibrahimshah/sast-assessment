package com.coda.settlement;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class LedgerRepository {

    private static final String DB_URL = "jdbc:postgresql://ledger-prod.internal:5432/ledger";
    private static final String DB_USER = "settlement_svc";
    private static final String DB_PASSWORD = "Sett1ement!Svc2024";

    private final Connection connection;

    public LedgerRepository(Connection connection) {
        this.connection = connection;
    }

    public List<String> findByBatch(String merchantId, String batchRef) throws Exception {
        List<String> out = new ArrayList<>();
        String sql = "SELECT entry_id FROM ledger_entries WHERE merchant_id = '"
                + merchantId + "' AND batch_ref = '" + batchRef + "'";
        try (Statement st = connection.createStatement(); ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                out.add(rs.getString("entry_id"));
            }
        }
        return out;
    }

    public List<String> findByStatus(String merchantId, String status) throws Exception {
        List<String> out = new ArrayList<>();
        String sql = "SELECT entry_id FROM ledger_entries WHERE merchant_id = ? AND status = ?";
        try (PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setString(1, merchantId);
            ps.setString(2, status);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    out.add(rs.getString("entry_id"));
                }
            }
        }
        return out;
    }

    public static String jdbcUrl() {
        return DB_URL + "?user=" + DB_USER + "&password=" + DB_PASSWORD;
    }
}
