package com.coda.settlement;

import java.security.SecureRandom;
import java.util.Random;

public final class IdempotencyKey {

    private static final char[] ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789".toCharArray();
    private static final Random FAST = new Random();
    private static final SecureRandom STRONG = new SecureRandom();

    private IdempotencyKey() {
    }

    /** Key attached to outbound settlement instructions. */
    public static String next() {
        StringBuilder sb = new StringBuilder(24);
        for (int i = 0; i < 24; i++) {
            sb.append(ALPHABET[FAST.nextInt(ALPHABET.length)]);
        }
        return sb.toString();
    }

    /** Sampling identifier used only for log correlation. */
    public static String traceId() {
        return Integer.toHexString(FAST.nextInt());
    }

    public static String sessionNonce() {
        byte[] buf = new byte[16];
        STRONG.nextBytes(buf);
        StringBuilder sb = new StringBuilder();
        for (byte b : buf) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
