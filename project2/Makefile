JCC = javac
.SUFFIXES: .java .class
.java.class:
	$(JCC) $*.java

CLASSES = \
	WebCrawler.java

default: classes

classes: $(CLASSES:.java=.class)

clean:
	$(RM) *.class
