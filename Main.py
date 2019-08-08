import netlistReader as nreader
import solver as solv


def main():

    reader = nreader.Reader()
    input_data = reader.readFile("Schaltung.txt")
    schaltung = nreader.Schaltung(input_data)
    schaltung.initInzidenzMatritzen()


    solver = solv.Solver(schaltung)
    solver.removeComponent("G")

if __name__ == "__main__":

    main()
    

