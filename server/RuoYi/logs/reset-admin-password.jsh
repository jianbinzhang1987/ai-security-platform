String url = "jdbc:mysql://47.105.65.4:13306/ry?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8";
try (var conn = java.sql.DriverManager.getConnection(url, "dbuser", "SecurePass2024");
     var stmt = conn.createStatement()) {
    int updated = stmt.executeUpdate("update sys_user set password='3d3e2e119996cedb7401025cced5c1b0', salt='111111', update_by='codex', update_time=now() where login_name='admin'");
    System.out.println("updated=" + updated);
}
/exit