import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;
import com.sun.source.util.JavacTask;

/** Parse-only check: catches syntax errors without pretending to compile the Android/LibGDX app. */
public final class JavaSyntaxCheck {
    public static void main(String[] args) throws Exception {
        List<File> files = new ArrayList<>();
        for (String root : args) visit(new File(root), files);
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        if (compiler == null) throw new IllegalStateException("JDK diperlukan");
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        try (StandardJavaFileManager fm = compiler.getStandardFileManager(diagnostics, null, null)) {
            Iterable<? extends JavaFileObject> sources = fm.getJavaFileObjectsFromFiles(files);
            JavacTask task = (JavacTask) compiler.getTask(null, fm, diagnostics, Arrays.asList("--release", "11", "-proc:none"), null, sources);
            task.parse();
        }
        int errors = 0;
        for (Diagnostic<? extends JavaFileObject> d : diagnostics.getDiagnostics()) {
            if (d.getKind() == Diagnostic.Kind.ERROR) {
                System.err.println(d.getSource() + ":" + d.getLineNumber() + " " + d.getMessage(null));
                errors++;
            }
        }
        if (errors > 0) throw new IllegalStateException(errors + " kesalahan syntax Java");
        System.out.println("Syntax OK: " + files.size() + " berkas Java diparse untuk Java 11 (tanpa type-link/runtime Android)");
    }
    private static void visit(File f, List<File> out) throws IOException {
        if (!f.exists()) throw new IOException("Folder tidak ditemukan: " + f);
        if (f.isDirectory()) {
            File[] children = f.listFiles();
            if (children != null) for (File c : children) visit(c, out);
        } else if (f.getName().endsWith(".java")) out.add(f);
    }
}
