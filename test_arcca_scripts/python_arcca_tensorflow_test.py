import sys
import tensorflow as tf

SLURM_JOB_ID = sys.argv[1]
SLURM_ARRAY_JOB_ID = sys.argv[2]
SLURM_ARRAY_TASK_ID = sys.argv[3]

print(SLURM_JOB_ID)
print(SLURM_ARRAY_JOB_ID)
print(SLURM_ARRAY_TASK_ID)

class SquareTest(tf.test.TestCase):
    def testSquare(self):
        with self.test_session():
            x = tf.square([2, 3])
            self.assertAllEqual(x.eval(), [4, 9])


if __name__ == '__main__':
    print("run tesnroflow test case")
    tf.test.main()
