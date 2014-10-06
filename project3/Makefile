JCC = javac
.SUFFIXES: .java .class
.java.class:
	$(JCC) $*.java

CLASSES = \
	Experiment1.java Experiment2.java

default: classes

classes: $(CLASSES:.java=.class)

clean:
	$(RM) *.class
