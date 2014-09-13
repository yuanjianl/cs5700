# define a makefile variable for the java compiler
#
JCC = javac

# define a makefile variable for compilation flags
# the -g flag compiles with debugging information
#
JFLAGS = -g

# typing 'make' will invoke the first target entry in the makefile 
# (the default one in this case)
#
default: Client.class

# this target entry builds the Client.class
#
Client.class: Client.java
		$(JCC) $(JFLAGS) Client.java

# To start over from scratch, type 'make clean'.  
# Removes all .class files, so that the next make rebuilds them
#
clean: 
		$(RM) *.class